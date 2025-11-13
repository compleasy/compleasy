import pytest
from django.test import Client
from django.urls import reverse
from api.models import LicenseKey, Device, FullReport, DiffReport


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
        assert response.content == b'Invalid license key'

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
