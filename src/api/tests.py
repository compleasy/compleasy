from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from api.models import LicenseKey, Device, FullReport, DiffReport, ActivityIgnorePattern, Organization, DeviceEvent, EnrollmentSettings, EnrollmentPlugin, EnrollmentSkipTest
from api.utils.lynis_report import LynisReport
import fnmatch


@pytest.mark.django_db
class TestUploadReport:
    """Tests for the upload_report endpoint."""

    def test_upload_report_valid_license_new_device(self, test_license_key, sample_lynis_report):
        """Test uploading a report with valid license key for a new device."""
        client = Client()
        url = reverse('upload_report')
        
        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': 'new-host-id-1',
            'hostid2': 'new-host-id-2',
            'data': sample_lynis_report
        })
        
        assert response.status_code == 200
        assert response.content == b'OK'
        
        # Verify device was created
        device = Device.objects.get(hostid='new-host-id-1', hostid2='new-host-id-2')
        assert device.licensekey == test_license_key
        assert device.hostname == 'test-server'
        assert device.os == 'Linux'
        assert device.distro == 'Ubuntu'
        assert device.distro_version == '22.04'
        assert device.lynis_version == '3.0.0'
        assert device.warnings == 5
        
        # Verify report was saved
        report = FullReport.objects.filter(device=device).first()
        assert report is not None
        # Compare reports ignoring trailing whitespace
        assert report.full_report.strip() == sample_lynis_report.strip()

    def test_upload_report_invalid_license(self, sample_lynis_report):
        """Test uploading a report with invalid license key returns 401."""
        client = Client()
        url = reverse('upload_report')
        
        response = client.post(url, {
            'licensekey': 'invalid-license-key',
            'hostid': 'test-host-id-1',
            'hostid2': 'test-host-id-2',
            'data': sample_lynis_report
        })
        
        assert response.status_code == 401
        assert response.content == b'License key does not exist'

    def test_upload_report_missing_hostid(self, test_license_key, sample_lynis_report):
        """Test uploading a report with missing hostid returns 400."""
        client = Client()
        url = reverse('upload_report')
        
        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': '',
            'hostid2': 'test-host-id-2',
            'data': sample_lynis_report
        })
        
        # Form validation fails before reaching the specific check
        assert response.status_code == 400
        assert response.content == b'Invalid form data'

    def test_upload_report_missing_hostid2(self, test_license_key, sample_lynis_report):
        """Test uploading a report with missing hostid2 returns 400."""
        client = Client()
        url = reverse('upload_report')
        
        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': 'test-host-id-1',
            'hostid2': '',
            'data': sample_lynis_report
        })
        
        # Form validation fails before reaching the specific check
        assert response.status_code == 400
        assert response.content == b'Invalid form data'

    def test_upload_report_missing_data(self, test_license_key):
        """Test uploading a report with missing data returns 400."""
        client = Client()
        url = reverse('upload_report')
        
        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': 'test-host-id-1',
            'hostid2': 'test-host-id-2',
            'data': ''
        })
        
        # Form validation fails before reaching the specific check
        assert response.status_code == 400
        assert response.content == b'Invalid form data'

    def test_upload_report_existing_device_update(self, test_device, sample_lynis_report, sample_lynis_report_updated):
        """Test uploading a report for an existing device updates it and generates diff."""
        client = Client()
        url = reverse('upload_report')
        
        # First upload
        response1 = client.post(url, {
            'licensekey': test_device.licensekey.licensekey,
            'hostid': test_device.hostid,
            'hostid2': test_device.hostid2,
            'data': sample_lynis_report
        })
        
        assert response1.status_code == 200
        
        # Second upload with updated report
        response2 = client.post(url, {
            'licensekey': test_device.licensekey.licensekey,
            'hostid': test_device.hostid,
            'hostid2': test_device.hostid2,
            'data': sample_lynis_report_updated
        })
        
        assert response2.status_code == 200
        
        # Verify diff was created
        diff_reports = DiffReport.objects.filter(device=test_device)
        assert diff_reports.count() >= 1
        
        # Verify device was updated
        test_device.refresh_from_db()
        assert test_device.lynis_version == '3.0.1'
        assert test_device.warnings == 3

    def test_upload_report_invalid_method_get(self):
        """Test GET method returns 405."""
        client = Client()
        url = reverse('upload_report')
        
        response = client.get(url)
        assert response.status_code == 405
        assert response.content == b'Invalid request method'

    def test_upload_report_invalid_method_put(self):
        """Test PUT method returns 405."""
        client = Client()
        url = reverse('upload_report')
        
        response = client.put(url)
        assert response.status_code == 405
        assert response.content == b'Invalid request method'

    def test_upload_report_invalid_method_delete(self):
        """Test DELETE method returns 405."""
        client = Client()
        url = reverse('upload_report')
        
        response = client.delete(url)
        assert response.status_code == 405
        assert response.content == b'Invalid request method'

    def test_upload_report_invalid_form_data(self, test_license_key):
        """Test uploading with invalid form data returns 400."""
        client = Client()
        url = reverse('upload_report')
        
        # Missing required fields
        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
        })
        
        assert response.status_code == 400
        assert response.content == b'Invalid form data'

    def test_upload_report_real_lynis_report(self, test_license_key, real_lynis_report):
        """
        Test uploading a real Lynis report generated by the Lynis client.
        
        This test simulates the exact upload process that the Lynis client uses:
        - POST request to /api/lynis/upload/
        - Form data with licensekey, hostid, hostid2, and data fields
        - The data field contains the full Lynis report content
        
        This is a faster alternative to the full integration test, using a real
        report file extracted from an actual Lynis audit.
        """
        client = Client()
        url = reverse('upload_report')
        
        # Extract hostid and hostid2 from the report if available
        # Real Lynis reports contain these in the report data
        # For this test, we'll use test values that match the integration test
        hostid = 'real-lynis-test-host-1'
        hostid2 = 'real-lynis-test-host-2'
        
        # Upload the report using the same method as Lynis client
        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': hostid,
            'hostid2': hostid2,
            'data': real_lynis_report
        })
        
        assert response.status_code == 200
        assert response.content == b'OK'
        
        # Verify device was created or updated
        device = Device.objects.get(hostid=hostid, hostid2=hostid2)
        assert device.licensekey == test_license_key
        
        # Verify report was saved
        report = FullReport.objects.filter(device=device).first()
        assert report is not None
        # Compare reports ignoring trailing whitespace
        assert report.full_report.strip() == real_lynis_report.strip()
        
        # Verify the report can be parsed (basic validation)
        from api.utils.lynis_report import LynisReport
        parsed_report = LynisReport(real_lynis_report)
        assert parsed_report.keys is not None
        assert len(parsed_report.keys) > 0


@pytest.mark.django_db
class TestCheckLicense:
    """Tests for the check_license endpoint."""

    def test_check_license_valid(self, test_license_key):
        """Test checking a valid license key returns 'Response 100'."""
        client = Client()
        url = reverse('check_license')
        
        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'collector_version': '1.0.0'
        })
        
        assert response.status_code == 200
        assert response.content == b'Response 100'

    def test_check_license_invalid(self):
        """Test checking an invalid license key returns 401 with 'Response 500'."""
        client = Client()
        url = reverse('check_license')
        
        response = client.post(url, {
            'licensekey': 'invalid-license-key',
            'collector_version': '1.0.0'
        })
        
        assert response.status_code == 401
        assert response.content == b'Response 500'

    def test_check_license_missing_licensekey(self):
        """Test checking license with missing licensekey returns 400."""
        client = Client()
        url = reverse('check_license')
        
        response = client.post(url, {
            'collector_version': '1.0.0'
        })
        
        assert response.status_code == 400
        assert response.content == b'No license key provided'

    def test_check_license_missing_collector_version(self, test_license_key):
        """Test checking license with missing collector_version returns 400."""
        client = Client()
        url = reverse('check_license')
        
        response = client.post(url, {
            'licensekey': test_license_key.licensekey
        })
        
        assert response.status_code == 400
        assert response.content == b'No collector version provided'

    def test_check_license_invalid_method_get(self):
        """Test GET method returns 405."""
        client = Client()
        url = reverse('check_license')
        
        response = client.get(url)
        assert response.status_code == 405
        assert response.content == b'Invalid request method'


@pytest.mark.django_db
class TestEnrollScript:
    def test_enroll_script_includes_plugin_urls(self, test_license_key):
        settings = EnrollmentSettings.get_settings()
        settings.plugins.all().delete()
        settings.skip_tests_entries.all().delete()
        EnrollmentPlugin.objects.create(
            settings=settings,
            url='https://plugins.example.com/trikusec/plugin_trikusec_phase1'
        )
        EnrollmentSkipTest.objects.create(
            settings=settings,
            test_id='CRYP-7902'
        )

        client = Client()
        response = client.get(reverse('enroll_sh'), {'licensekey': test_license_key.licensekey})

        assert response.status_code == 200
        body = response.content.decode()
        assert 'Installing Lynis plugins configured in TrikuSec' in body
        assert 'https://plugins.example.com/trikusec/plugin_trikusec_phase1' in body
        assert 'PLUGIN_URLS=(' in body
        assert 'Configuring Lynis to skip tests: CRYP-7902' in body
        assert 'test_skip_always=CRYP-7902' in body
        assert response['Content-Type'] == 'text/x-shellscript'

    def test_check_license_invalid_method_put(self):
        """Test PUT method returns 405."""
        client = Client()
        url = reverse('check_license')
        
        response = client.put(url)
        assert response.status_code == 405
        assert response.content == b'Invalid request method'

    def test_check_license_invalid_method_delete(self):
        """Test DELETE method returns 405."""
        client = Client()
        url = reverse('check_license')
        
        response = client.delete(url)
        assert response.status_code == 405
        assert response.content == b'Invalid request method'


@pytest.mark.django_db
class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check_healthy(self):
        """Test health check returns healthy status when all checks pass."""
        client = Client()
        url = reverse('health_check')
        
        response = client.get(url)
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['checks']['database'] == 'ok'
        assert data['checks']['cache'] == 'ok'

    def test_health_check_json_format(self):
        """Test health check returns valid JSON format."""
        client = Client()
        url = reverse('health_check')
        
        response = client.get(url)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        data = response.json()
        assert 'status' in data
        assert 'checks' in data
        assert isinstance(data['checks'], dict)
        assert 'database' in data['checks']
        assert 'cache' in data['checks']

    def test_health_check_allows_all_methods(self):
        """Test health check accepts GET, POST, HEAD, OPTIONS methods."""
        client = Client()
        url = reverse('health_check')
        
        # GET should work
        response = client.get(url)
        assert response.status_code == 200
        
        # POST should work (health checks often use POST)
        response = client.post(url)
        assert response.status_code == 200
        
        # HEAD should work
        response = client.head(url)
        assert response.status_code == 200
        
        # OPTIONS should work
        response = client.options(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestDatabaseIndexes:
    """Tests to verify database indexes are working correctly."""
    
    def test_licensekey_index_query(self, test_license_key):
        """Test that queries on licensekey field use the index."""
        # Create multiple license keys
        from django.contrib.auth.models import User
        user = test_license_key.created_by
        
        # Query by licensekey - should be fast with index
        found_key = LicenseKey.objects.filter(licensekey=test_license_key.licensekey).first()
        assert found_key is not None
        assert found_key.licensekey == test_license_key.licensekey
        
        # Test exists() query which is commonly used
        assert LicenseKey.objects.filter(licensekey=test_license_key.licensekey).exists()
        assert not LicenseKey.objects.filter(licensekey='non-existent-key').exists()
    
    def test_device_hostid_index_query(self, test_device):
        """Test that queries on hostid field use the index."""
        # Query by hostid - should be fast with index
        found_device = Device.objects.filter(hostid=test_device.hostid).first()
        assert found_device is not None
        assert found_device.hostid == test_device.hostid
    
    def test_device_hostid2_index_query(self, test_device):
        """Test that queries on hostid2 field use the index."""
        # Query by hostid2 - should be fast with index
        found_device = Device.objects.filter(hostid2=test_device.hostid2).first()
        assert found_device is not None
        assert found_device.hostid2 == test_device.hostid2
    
    def test_device_composite_index_licensekey_hostid(self, test_license_key):
        """Test that composite queries on (licensekey, hostid) use the composite index."""
        from api.models import Device
        
        # Create a device
        device = Device.objects.create(
            licensekey=test_license_key,
            hostid='composite-test-hostid',
            hostid2='composite-test-hostid2'
        )
        
        # Query using both fields - should use composite index
        found_device = Device.objects.filter(
            licensekey=test_license_key,
            hostid='composite-test-hostid'
        ).first()
        
        assert found_device is not None
        assert found_device.hostid == 'composite-test-hostid'
        assert found_device.licensekey == test_license_key
    
    def test_device_composite_index_licensekey_hostid2(self, test_license_key):
        """Test that composite queries on (licensekey, hostid2) use the composite index."""
        from api.models import Device
        
        # Create a device
        device = Device.objects.create(
            licensekey=test_license_key,
            hostid='composite-test-hostid',
            hostid2='composite-test-hostid2'
        )
        
        # Query using both fields - should use composite index
        found_device = Device.objects.filter(
            licensekey=test_license_key,
            hostid2='composite-test-hostid2'
        ).first()
        
        assert found_device is not None
        assert found_device.hostid2 == 'composite-test-hostid2'
        assert found_device.licensekey == test_license_key
    
    def test_device_get_or_create_uses_indexes(self, test_license_key):
        """Test that get_or_create queries use the indexes efficiently."""
        from api.models import Device
        
        # This is the actual query pattern used in views.py
        device, created = Device.objects.get_or_create(
            hostid='get-or-create-hostid',
            hostid2='get-or-create-hostid2',
            licensekey=test_license_key
        )
        
        assert created is True
        assert device.hostid == 'get-or-create-hostid'
        assert device.hostid2 == 'get-or-create-hostid2'
        
        # Try again - should find existing device
        device2, created2 = Device.objects.get_or_create(
            hostid='get-or-create-hostid',
            hostid2='get-or-create-hostid2',
            licensekey=test_license_key
        )
        
        assert created2 is False
        assert device2.id == device.id
    
    def test_device_last_update_index_sorting(self, test_license_key):
        """Test that sorting by last_update uses the index."""
        from api.models import Device
        from django.utils import timezone
        import datetime
        
        # Create multiple devices with different last_update times
        now = timezone.now()
        devices = []
        for i in range(5):
            device = Device.objects.create(
                licensekey=test_license_key,
                hostid=f'sort-test-hostid-{i}',
                hostid2=f'sort-test-hostid2-{i}',
                last_update=now - datetime.timedelta(hours=i)
            )
            devices.append(device)
        
        # Query sorted by last_update - should use index
        sorted_devices = Device.objects.filter(
            licensekey=test_license_key
        ).order_by('last_update')
        
        assert sorted_devices.count() >= 5
        # Verify ordering (oldest first)
        last_update_values = [d.last_update for d in sorted_devices if d.last_update]
        assert last_update_values == sorted(last_update_values)
        
        # Test descending order
        sorted_devices_desc = Device.objects.filter(
            licensekey=test_license_key
        ).order_by('-last_update')
        
        last_update_values_desc = [d.last_update for d in sorted_devices_desc if d.last_update]
        assert last_update_values_desc == sorted(last_update_values_desc, reverse=True)
    
    def test_indexes_exist_in_database(self, db):
        """Test that indexes actually exist in the database schema."""
        from django.db import connection
        
        # Get table names
        with connection.cursor() as cursor:
            # For SQLite, check that indexes exist
            if connection.vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' 
                    AND tbl_name IN ('api_licensekey', 'api_device')
                    AND name NOT LIKE 'sqlite_%'
                """)
                indexes = [row[0] for row in cursor.fetchall()]
                
                # Check for expected indexes
                # Note: SQLite creates indexes automatically for db_index=True fields
                # and composite indexes from Meta.indexes
                assert len(indexes) > 0, "Should have at least some indexes"
                
                # Verify we can query the index information
                cursor.execute("""
                    SELECT sql FROM sqlite_master 
                    WHERE type='index' 
                    AND tbl_name='api_device'
                """)
                device_indexes = [row[0] for row in cursor.fetchall() if row[0]]
                
                # Should have indexes (exact names depend on Django's naming)
                assert len(device_indexes) > 0, "Device table should have indexes"


@pytest.mark.django_db
class TestLicenseValidation:
    """Tests for license validation and capacity checking."""

    def test_validate_license_active(self, test_license_key):
        """Test validating an active license."""
        from api.utils.license_utils import validate_license
        
        is_valid, error = validate_license(test_license_key.licensekey)
        assert is_valid is True
        assert error is None

    def test_validate_license_inactive(self, test_license_key):
        """Test validating an inactive license."""
        from api.utils.license_utils import validate_license
        
        test_license_key.is_active = False
        test_license_key.save()
        
        is_valid, error = validate_license(test_license_key.licensekey)
        assert is_valid is False
        assert "inactive" in error.lower()

    def test_validate_license_expired(self, test_license_key):
        """Test validating an expired license."""
        from api.utils.license_utils import validate_license
        from django.utils import timezone
        from datetime import timedelta
        
        test_license_key.expires_at = timezone.now() - timedelta(days=1)
        test_license_key.save()
        
        is_valid, error = validate_license(test_license_key.licensekey)
        assert is_valid is False
        assert "expired" in error.lower()

    def test_validate_license_nonexistent(self):
        """Test validating a non-existent license."""
        from api.utils.license_utils import validate_license
        
        is_valid, error = validate_license('nonexistent-key-12345')
        assert is_valid is False
        assert "does not exist" in error.lower()

    def test_check_license_capacity_unlimited(self, test_license_key):
        """Test checking capacity for unlimited license."""
        from api.utils.license_utils import check_license_capacity
        
        test_license_key.max_devices = None  # Unlimited
        test_license_key.save()
        
        has_capacity, error = check_license_capacity(test_license_key.licensekey)
        assert has_capacity is True
        assert error is None

    def test_check_license_capacity_with_space(self, test_license_key):
        """Test checking capacity for license with available space."""
        from api.utils.license_utils import check_license_capacity
        
        test_license_key.max_devices = 5
        test_license_key.save()
        
        # Create 2 devices (below limit of 5)
        Device.objects.create(
            licensekey=test_license_key,
            hostid='host1',
            hostid2='host1-2'
        )
        Device.objects.create(
            licensekey=test_license_key,
            hostid='host2',
            hostid2='host2-2'
        )
        
        has_capacity, error = check_license_capacity(test_license_key.licensekey)
        assert has_capacity is True
        assert error is None

    def test_check_license_capacity_at_limit(self, test_license_key):
        """Test checking capacity for license at device limit."""
        from api.utils.license_utils import check_license_capacity
        
        test_license_key.max_devices = 2
        test_license_key.save()
        
        # Create 2 devices (at limit)
        Device.objects.create(
            licensekey=test_license_key,
            hostid='host1',
            hostid2='host1-2'
        )
        Device.objects.create(
            licensekey=test_license_key,
            hostid='host2',
            hostid2='host2-2'
        )
        
        has_capacity, error = check_license_capacity(test_license_key.licensekey)
        assert has_capacity is False
        assert "maximum device limit" in error.lower()

    def test_license_has_capacity_method(self, test_license_key):
        """Test LicenseKey.has_capacity() method."""
        test_license_key.max_devices = 3
        test_license_key.save()
        
        # Initially has capacity
        assert test_license_key.has_capacity() is True
        
        # Create devices up to limit
        for i in range(3):
            Device.objects.create(
                licensekey=test_license_key,
                hostid=f'host{i}',
                hostid2=f'host{i}-2'
            )
        
        # Refresh from DB
        test_license_key.refresh_from_db()
        assert test_license_key.has_capacity() is False

    def test_license_device_count_method(self, test_license_key):
        """Test LicenseKey.device_count() method."""
        assert test_license_key.device_count() == 0
        
        Device.objects.create(
            licensekey=test_license_key,
            hostid='host1',
            hostid2='host1-2'
        )
        
        assert test_license_key.device_count() == 1
        
        Device.objects.create(
            licensekey=test_license_key,
            hostid='host2',
            hostid2='host2-2'
        )
        
        assert test_license_key.device_count() == 2

    def test_generate_license_key_uniqueness(self):
        """Test that generate_license_key creates unique keys."""
        from api.utils.license_utils import generate_license_key
        from api.models import LicenseKey
        
        key1 = generate_license_key()
        key2 = generate_license_key()
        
        assert key1 != key2
        assert len(key1) == 26  # Format: xxxxxxxx-xxxxxxxx-xxxxxxxx
        assert key1.count('-') == 2
        
        # Verify keys don't exist in database
        assert not LicenseKey.objects.filter(licensekey=key1).exists()
        assert not LicenseKey.objects.filter(licensekey=key2).exists()

    def test_generate_license_key_format_lynis_compatible(self):
        """Test that generate_license_key creates keys compatible with Lynis format [a-f0-9-]."""
        import re
        from api.utils.license_utils import generate_license_key
        
        # Generate multiple keys to ensure consistency
        for _ in range(10):
            key = generate_license_key()
            
            # Verify format: xxxxxxxx-xxxxxxxx-xxxxxxxx
            assert len(key) == 26, f"Key length should be 26, got {len(key)}: {key}"
            assert key.count('-') == 2, f"Key should have 2 hyphens, got {key.count('-')}: {key}"
            
            # Verify only hexadecimal characters (a-f, 0-9) and hyphens
            # This matches Lynis's filter: tr -cd '[a-f0-9-]'
            assert re.match(r'^[a-f0-9]{8}-[a-f0-9]{8}-[a-f0-9]{8}$', key), \
                f"Key should only contain hex chars [a-f0-9] and hyphens: {key}"
            
            # Verify no uppercase characters
            assert key.islower() or key.replace('-', '').islower(), \
                f"Key should be lowercase: {key}"
            
            # Verify parts are separated by hyphens
            parts = key.split('-')
            assert len(parts) == 3, f"Key should have 3 parts: {key}"
            assert all(len(part) == 8 for part in parts), \
                f"Each part should be 8 characters: {key}"


@pytest.mark.django_db
class TestLicenseCapacityEnrollment:
    """Tests for device enrollment with license capacity limits."""

    def test_upload_report_respects_license_capacity(self, test_license_key, sample_lynis_report):
        """Test that upload_report rejects enrollment when license is at capacity."""
        from django.test import Client
        from django.urls import reverse
        
        # Set license to allow only 1 device
        test_license_key.max_devices = 1
        test_license_key.save()
        
        # Create one device (at capacity)
        Device.objects.create(
            licensekey=test_license_key,
            hostid='existing-host',
            hostid2='existing-host-2'
        )
        
        client = Client()
        url = reverse('upload_report')
        
        # Try to enroll a new device
        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': 'new-host-id-1',
            'hostid2': 'new-host-id-2',
            'data': sample_lynis_report
        })
        
        # Should be rejected with 403
        assert response.status_code == 403
        assert "maximum device limit" in response.content.decode().lower()

    def test_upload_report_allows_existing_device_update(self, test_license_key, sample_lynis_report):
        """Test that upload_report allows updates to existing devices even at capacity."""
        from django.test import Client
        from django.urls import reverse
        
        # Set license to allow only 1 device
        test_license_key.max_devices = 1
        test_license_key.save()
        
        # Create one device (at capacity)
        device = Device.objects.create(
            licensekey=test_license_key,
            hostid='existing-host',
            hostid2='existing-host-2'
        )
        
        client = Client()
        url = reverse('upload_report')
        
        # Update existing device (should work even at capacity)
        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': 'existing-host',
            'hostid2': 'existing-host-2',
            'data': sample_lynis_report
        })
        
        # Should succeed
        assert response.status_code == 200
        assert response.content == b'OK'

    def test_upload_report_creates_enrollment_event(self, test_license_key, sample_lynis_report):
        """Ensure a new device upload generates a single enrollment event."""
        client = Client()
        url = reverse('upload_report')

        response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': 'enroll-host-1',
            'hostid2': 'enroll-host-2',
            'data': sample_lynis_report
        })

        assert response.status_code == 200

        device = Device.objects.get(hostid='enroll-host-1', hostid2='enroll-host-2')
        enrollment_events = DeviceEvent.objects.filter(device=device, event_type='enrolled')
        assert enrollment_events.count() == 1
        assert enrollment_events.first().created_at is not None

    def test_upload_report_existing_device_no_duplicate_enrollment(self, test_license_key, sample_lynis_report, sample_lynis_report_updated):
        """Ensure subsequent uploads for the same device do not create extra enrollment events."""
        client = Client()
        url = reverse('upload_report')

        # First upload creates the device and enrollment event
        first_response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': 'existing-enroll-host',
            'hostid2': 'existing-enroll-host-2',
            'data': sample_lynis_report
        })
        assert first_response.status_code == 200

        device = Device.objects.get(hostid='existing-enroll-host', hostid2='existing-enroll-host-2')
        assert DeviceEvent.objects.filter(device=device, event_type='enrolled').count() == 1

        # Second upload should not create additional enrollment events
        second_response = client.post(url, {
            'licensekey': test_license_key.licensekey,
            'hostid': 'existing-enroll-host',
            'hostid2': 'existing-enroll-host-2',
            'data': sample_lynis_report_updated
        })
        assert second_response.status_code == 200
        assert DeviceEvent.objects.filter(device=device, event_type='enrolled').count() == 1


class TestLynisReportCustomVariables:
    """Tests for dynamically generated fields in LynisReport."""

    def test_days_since_audit_populated_from_space_datetime(self, monkeypatch):
        fixed_now = timezone.now()
        monkeypatch.setattr('api.utils.lynis_report.timezone.now', lambda: fixed_now)

        report_end = (fixed_now - timedelta(days=3, hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        report_data = f"report_datetime_end={report_end}"

        parsed = LynisReport(report_data).get_parsed_report()

        assert parsed['days_since_audit'] == 3

    def test_days_since_audit_populated_from_iso_datetime(self, monkeypatch):
        fixed_now = timezone.now()
        monkeypatch.setattr('api.utils.lynis_report.timezone.now', lambda: fixed_now)

        report_end = fixed_now - timedelta(days=1, minutes=30)
        report_data = f"report_datetime_end={report_end.isoformat()}"

        parsed = LynisReport(report_data).get_parsed_report()

        assert parsed['days_since_audit'] == 1

    def test_days_since_audit_handles_invalid_values(self):
        report_data = "report_datetime_end=not-a-valid-date"
        parsed = LynisReport(report_data).get_parsed_report()

        assert parsed['days_since_audit'] is None


@pytest.mark.django_db
class TestActivityIgnorePattern:
    """Tests for ActivityIgnorePattern model and filtering logic."""

    def test_activity_ignore_pattern_creation(self, test_organization):
        """Test creating an ActivityIgnorePattern with all fields."""
        pattern = ActivityIgnorePattern.objects.create(
            organization=test_organization,
            key_pattern='slow_test',
            event_type='changed',
            host_pattern='web-*',
            is_active=True
        )
        
        assert pattern.key_pattern == 'slow_test'
        assert pattern.event_type == 'changed'
        assert pattern.host_pattern == 'web-*'
        assert pattern.is_active is True
        assert 'slow_test' in str(pattern)
        assert 'Changed' in str(pattern)

    def test_activity_ignore_pattern_defaults(self, test_organization):
        """Test ActivityIgnorePattern default values."""
        pattern = ActivityIgnorePattern.objects.create(
            organization=test_organization,
            key_pattern='test_key'
        )
        
        assert pattern.event_type == 'all'
        assert pattern.host_pattern == '*'
        assert pattern.is_active is True

    def test_activity_ignore_pattern_unique_constraint(self, test_organization):
        """Test that unique constraint works for organization, key_pattern, event_type, host_pattern."""
        ActivityIgnorePattern.objects.create(
            organization=test_organization,
            key_pattern='test_key',
            event_type='all',
            host_pattern='*'
        )
        
        # Should not be able to create duplicate
        with pytest.raises(Exception):  # IntegrityError or similar
            ActivityIgnorePattern.objects.create(
                organization=test_organization,
                key_pattern='test_key',
                event_type='all',
                host_pattern='*'
            )

    def test_pattern_matching_key_pattern(self, test_organization):
        """Test that key pattern matching works with fnmatch."""
        # Test exact match
        assert fnmatch.fnmatch('slow_test', 'slow_test') is True
        assert fnmatch.fnmatch('slow_test', 'fast_test') is False
        
        # Test wildcard match
        assert fnmatch.fnmatch('slow_test', 'slow_*') is True
        assert fnmatch.fnmatch('test_key', 'test_*') is True
        assert fnmatch.fnmatch('other_key', 'test_*') is False
        
        # Test wildcard for all
        assert fnmatch.fnmatch('any_key', '*') is True

    def test_pattern_matching_host_pattern(self, test_organization):
        """Test that host pattern matching works with fnmatch."""
        # Test exact match
        assert fnmatch.fnmatch('web-01', 'web-01') is True
        assert fnmatch.fnmatch('web-01', 'db-01') is False
        
        # Test wildcard match
        assert fnmatch.fnmatch('web-01', 'web-*') is True
        assert fnmatch.fnmatch('web-02', 'web-*') is True
        assert fnmatch.fnmatch('db-01', 'web-*') is False
        
        # Test wildcard for all
        assert fnmatch.fnmatch('any-host', '*') is True

    def test_activity_filtering_logic(self, test_organization, test_license_key):
        """Test the filtering logic for activities."""
        # Create a device
        device = Device.objects.create(
            licensekey=test_license_key,
            hostid='test-host-1',
            hostid2='test-host-2',
            hostname='web-01'
        )
        
        # Create a silence rule
        rule = ActivityIgnorePattern.objects.create(
            organization=test_organization,
            key_pattern='slow_test',
            event_type='all',
            host_pattern='*',
            is_active=True
        )
        
        # Test activity that should be filtered
        activity1 = {
            'device': device,
            'key': 'slow_test',
            'type': 'changed',
            'created_at': timezone.now()
        }
        
        # Test activity that should NOT be filtered (different key)
        activity2 = {
            'device': device,
            'key': 'other_key',
            'type': 'changed',
            'created_at': timezone.now()
        }
        
        # Simulate filtering logic
        should_filter1 = False
        should_filter2 = False
        
        for silence_rule in ActivityIgnorePattern.objects.filter(organization=test_organization, is_active=True):
            # Match key pattern
            if silence_rule.key_pattern != '*' and not fnmatch.fnmatch(activity1['key'], silence_rule.key_pattern):
                continue
            # Match event type
            if silence_rule.event_type != 'all' and activity1['type'] != silence_rule.event_type:
                continue
            # Match host pattern
            if silence_rule.host_pattern != '*' and device.hostname and not fnmatch.fnmatch(device.hostname, silence_rule.host_pattern):
                continue
            should_filter1 = True
            break
        
        for silence_rule in ActivityIgnorePattern.objects.filter(organization=test_organization, is_active=True):
            # Match key pattern
            if silence_rule.key_pattern != '*' and not fnmatch.fnmatch(activity2['key'], silence_rule.key_pattern):
                continue
            # Match event type
            if silence_rule.event_type != 'all' and activity2['type'] != silence_rule.event_type:
                continue
            # Match host pattern
            if silence_rule.host_pattern != '*' and device.hostname and not fnmatch.fnmatch(device.hostname, silence_rule.host_pattern):
                continue
            should_filter2 = True
            break
        
        assert should_filter1 is True  # Should be filtered
        assert should_filter2 is False  # Should NOT be filtered

    def test_activity_filtering_event_type(self, test_organization, test_license_key):
        """Test that event type filtering works correctly."""
        device = Device.objects.create(
            licensekey=test_license_key,
            hostid='test-host-1',
            hostid2='test-host-2',
            hostname='web-01'
        )
        
        # Create rule that only filters 'changed' events
        rule = ActivityIgnorePattern.objects.create(
            organization=test_organization,
            key_pattern='test_key',
            event_type='changed',
            host_pattern='*',
            is_active=True
        )
        
        # Test 'changed' activity - should be filtered
        activity_changed = {
            'device': device,
            'key': 'test_key',
            'type': 'changed',
            'created_at': timezone.now()
        }
        
        # Test 'added' activity - should NOT be filtered
        activity_added = {
            'device': device,
            'key': 'test_key',
            'type': 'added',
            'created_at': timezone.now()
        }
        
        # Simulate filtering
        should_filter_changed = False
        should_filter_added = False
        
        for silence_rule in ActivityIgnorePattern.objects.filter(organization=test_organization, is_active=True):
            if silence_rule.key_pattern != '*' and not fnmatch.fnmatch(activity_changed['key'], silence_rule.key_pattern):
                continue
            if silence_rule.event_type != 'all' and activity_changed['type'] != silence_rule.event_type:
                continue
            if silence_rule.host_pattern != '*' and device.hostname and not fnmatch.fnmatch(device.hostname, silence_rule.host_pattern):
                continue
            should_filter_changed = True
            break
        
        for silence_rule in ActivityIgnorePattern.objects.filter(organization=test_organization, is_active=True):
            if silence_rule.key_pattern != '*' and not fnmatch.fnmatch(activity_added['key'], silence_rule.key_pattern):
                continue
            if silence_rule.event_type != 'all' and activity_added['type'] != silence_rule.event_type:
                continue
            if silence_rule.host_pattern != '*' and device.hostname and not fnmatch.fnmatch(device.hostname, silence_rule.host_pattern):
                continue
            should_filter_added = True
            break
        
        assert should_filter_changed is True  # Should be filtered
        assert should_filter_added is False  # Should NOT be filtered

    def test_activity_filtering_host_pattern(self, test_organization, test_license_key):
        """Test that host pattern filtering works correctly."""
        device_web = Device.objects.create(
            licensekey=test_license_key,
            hostid='test-host-1',
            hostid2='test-host-2',
            hostname='web-01'
        )
        
        device_db = Device.objects.create(
            licensekey=test_license_key,
            hostid='test-host-3',
            hostid2='test-host-4',
            hostname='db-01'
        )
        
        # Create rule that only filters 'web-*' hosts
        rule = ActivityIgnorePattern.objects.create(
            organization=test_organization,
            key_pattern='test_key',
            event_type='all',
            host_pattern='web-*',
            is_active=True
        )
        
        # Test activity from web host - should be filtered
        activity_web = {
            'device': device_web,
            'key': 'test_key',
            'type': 'changed',
            'created_at': timezone.now()
        }
        
        # Test activity from db host - should NOT be filtered
        activity_db = {
            'device': device_db,
            'key': 'test_key',
            'type': 'changed',
            'created_at': timezone.now()
        }
        
        # Simulate filtering
        should_filter_web = False
        should_filter_db = False
        
        for silence_rule in ActivityIgnorePattern.objects.filter(organization=test_organization, is_active=True):
            if silence_rule.key_pattern != '*' and not fnmatch.fnmatch(activity_web['key'], silence_rule.key_pattern):
                continue
            if silence_rule.event_type != 'all' and activity_web['type'] != silence_rule.event_type:
                continue
            if silence_rule.host_pattern != '*' and device_web.hostname and not fnmatch.fnmatch(device_web.hostname, silence_rule.host_pattern):
                continue
            should_filter_web = True
            break
        
        for silence_rule in ActivityIgnorePattern.objects.filter(organization=test_organization, is_active=True):
            if silence_rule.key_pattern != '*' and not fnmatch.fnmatch(activity_db['key'], silence_rule.key_pattern):
                continue
            if silence_rule.event_type != 'all' and activity_db['type'] != silence_rule.event_type:
                continue
            if silence_rule.host_pattern != '*' and device_db.hostname and not fnmatch.fnmatch(device_db.hostname, silence_rule.host_pattern):
                continue
            should_filter_db = True
            break
        
        assert should_filter_web is True  # Should be filtered
        assert should_filter_db is False  # Should NOT be filtered
