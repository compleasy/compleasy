"""
Integration tests for end-to-end Lynis workflow.

These tests require Docker setup and are designed to test the full
Lynis integration workflow including:
- License validation
- Report upload
- Diff generation
- Device management

Note: These tests are marked with pytest.mark.integration and should
be run separately from unit tests, typically via CI/CD or manual execution
with docker compose.
"""
import pytest
import requests
import time
from api.models import LicenseKey, Device, FullReport, DiffReport


@pytest.mark.integration
@pytest.mark.django_db
class TestLynisIntegration:
    """Integration tests for Lynis workflow."""

    @pytest.fixture
    def server_url(self):
        """Get the Compleasy server URL from environment or use default."""
        import os
        return os.environ.get('COMPLEASY_SERVER_URL', 'http://localhost:8000')

    @pytest.fixture
    def test_license_key(self, db, test_user):
        """Create a test license key for integration testing."""
        from api.models import LicenseKey
        license_key = LicenseKey.objects.create(
            licensekey='integration-test-license-key',
            created_by=test_user
        )
        return license_key

    def test_server_health_check(self, server_url):
        """Test that the server is accessible."""
        try:
            response = requests.get(f"{server_url}/api/", timeout=5)
            # Any response (even 404) means server is up
            assert response.status_code in [200, 404]
        except requests.exceptions.RequestException:
            pytest.skip("Server not available for integration testing")

    def test_license_validation_endpoint(self, server_url, test_license_key):
        """Test license validation endpoint responds correctly."""
        try:
            response = requests.post(
                f"{server_url}/api/lynis/license/",
                data={
                    'licensekey': test_license_key.licensekey,
                    'collector_version': '1.0.0'
                },
                timeout=5
            )
            assert response.status_code == 200
            assert response.text == 'Response 100'
        except requests.exceptions.RequestException:
            pytest.skip("Server not available for integration testing")

    def test_license_validation_invalid_key(self, server_url):
        """Test license validation with invalid key."""
        try:
            response = requests.post(
                f"{server_url}/api/lynis/license/",
                data={
                    'licensekey': 'invalid-license-key',
                    'collector_version': '1.0.0'
                },
                timeout=5
            )
            assert response.status_code == 401
            assert response.text == 'Response 500'
        except requests.exceptions.RequestException:
            pytest.skip("Server not available for integration testing")

    def test_report_upload_workflow(self, server_url, test_license_key, sample_lynis_report):
        """Test complete report upload workflow."""
        try:
            # Upload report
            response = requests.post(
                f"{server_url}/api/lynis/upload/",
                data={
                    'licensekey': test_license_key.licensekey,
                    'hostid': 'integration-test-host-1',
                    'hostid2': 'integration-test-host-2',
                    'data': sample_lynis_report
                },
                timeout=10
            )
            assert response.status_code == 200
            assert response.text == 'OK'

            # Verify device was created
            device = Device.objects.get(
                hostid='integration-test-host-1',
                hostid2='integration-test-host-2'
            )
            assert device.licensekey == test_license_key
            assert device.hostname == 'test-server'

            # Verify report was saved
            report = FullReport.objects.filter(device=device).first()
            assert report is not None
            assert report.full_report == sample_lynis_report

        except requests.exceptions.RequestException:
            pytest.skip("Server not available for integration testing")

    def test_diff_generation_workflow(
        self, server_url, test_license_key, 
        sample_lynis_report, sample_lynis_report_updated
    ):
        """Test diff generation when uploading second report."""
        try:
            hostid = 'integration-test-host-diff-1'
            hostid2 = 'integration-test-host-diff-2'

            # First upload
            response1 = requests.post(
                f"{server_url}/api/lynis/upload/",
                data={
                    'licensekey': test_license_key.licensekey,
                    'hostid': hostid,
                    'hostid2': hostid2,
                    'data': sample_lynis_report
                },
                timeout=10
            )
            assert response1.status_code == 200

            # Wait a bit
            time.sleep(1)

            # Second upload with updated report
            response2 = requests.post(
                f"{server_url}/api/lynis/upload/",
                data={
                    'licensekey': test_license_key.licensekey,
                    'hostid': hostid,
                    'hostid2': hostid2,
                    'data': sample_lynis_report_updated
                },
                timeout=10
            )
            assert response2.status_code == 200

            # Verify diff was created
            device = Device.objects.get(hostid=hostid, hostid2=hostid2)
            diff_reports = DiffReport.objects.filter(device=device)
            assert diff_reports.count() >= 1

            # Verify device was updated
            device.refresh_from_db()
            assert device.lynis_version == '3.0.1'
            assert device.warnings == 3

        except requests.exceptions.RequestException:
            pytest.skip("Server not available for integration testing")

