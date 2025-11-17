import pytest
import json
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from api.models import Device, FullReport


@pytest.mark.django_db
class TestDeviceDelete:
    """Tests for the device_delete endpoint."""

    def test_delete_device_ajax_success(self, test_user, test_device):
        """Test deleting a device with AJAX request returns JSON success."""
        client = Client()
        client.force_login(test_user)
        
        device_id = test_device.id
        url = reverse('device_delete', kwargs={'device_id': device_id})
        
        # Create a report to verify CASCADE deletion
        FullReport.objects.create(
            device=test_device,
            full_report='# Test report\nhostname=test-device'
        )
        
        response = client.post(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['message'] == 'Device deleted successfully'
        
        # Verify device was deleted
        assert not Device.objects.filter(id=device_id).exists()
        
        # Verify reports were CASCADE deleted
        assert not FullReport.objects.filter(device_id=device_id).exists()

    def test_delete_device_traditional_success(self, test_user, test_device):
        """Test deleting a device with traditional request redirects to device list."""
        client = Client()
        client.force_login(test_user)
        
        device_id = test_device.id
        url = reverse('device_delete', kwargs={'device_id': device_id})
        
        response = client.post(url)
        
        assert response.status_code == 302  # Redirect
        assert response.url == reverse('device_list')
        
        # Verify device was deleted
        assert not Device.objects.filter(id=device_id).exists()

    def test_delete_device_invalid_id(self, test_user):
        """Test deleting a device with invalid ID returns 404."""
        client = Client()
        client.force_login(test_user)
        
        url = reverse('device_delete', kwargs={'device_id': 99999})
        
        response = client.post(url)
        
        assert response.status_code == 404

    def test_delete_device_get_method(self, test_user, test_device):
        """Test GET method returns 405 Method Not Allowed."""
        client = Client()
        client.force_login(test_user)
        
        url = reverse('device_delete', kwargs={'device_id': test_device.id})
        
        response = client.get(url)
        
        assert response.status_code == 405
        assert response.content == b'Method not allowed'

    def test_delete_device_unauthorized(self, test_device):
        """Test unauthenticated user cannot delete device."""
        client = Client()
        
        url = reverse('device_delete', kwargs={'device_id': test_device.id})
        
        response = client.post(url)
        
        # Should redirect to login page
        assert response.status_code == 302
        assert '/login' in response.url

    def test_delete_device_cascade_reports(self, test_user, test_device):
        """Test that deleting a device also deletes associated reports."""
        client = Client()
        client.force_login(test_user)
        
        device_id = test_device.id
        
        # Create multiple reports
        FullReport.objects.create(
            device=test_device,
            full_report='# Report 1\nhostname=test-device'
        )
        FullReport.objects.create(
            device=test_device,
            full_report='# Report 2\nhostname=test-device'
        )
        
        assert FullReport.objects.filter(device=test_device).count() == 2
        
        url = reverse('device_delete', kwargs={'device_id': device_id})
        response = client.post(url)
        
        assert response.status_code == 302
        
        # Verify all reports were deleted
        assert FullReport.objects.filter(device_id=device_id).count() == 0


@pytest.mark.django_db
class TestDeviceExportPDF:
    """Tests for the device_export_pdf endpoint."""

    def test_export_pdf_success(self, test_user, test_device, sample_lynis_report):
        """Test exporting PDF successfully returns PDF content."""
        client = Client()
        client.force_login(test_user)
        
        # Create a full report for the device
        FullReport.objects.create(
            device=test_device,
            full_report=sample_lynis_report
        )
        
        url = reverse('device_export_pdf', kwargs={'device_id': test_device.id})
        response = client.get(url)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert 'Content-Disposition' in response
        assert 'attachment' in response['Content-Disposition']
        
        # Verify PDF content is not empty
        assert len(response.content) > 0
        
        # Verify filename format
        assert 'device-' in response['Content-Disposition']
        assert '.pdf' in response['Content-Disposition']

    def test_export_pdf_filename_format(self, test_user, test_device, sample_lynis_report):
        """Test PDF filename includes hostname and timestamp."""
        client = Client()
        client.force_login(test_user)
        
        # Create a full report for the device
        FullReport.objects.create(
            device=test_device,
            full_report=sample_lynis_report
        )
        
        url = reverse('device_export_pdf', kwargs={'device_id': test_device.id})
        response = client.get(url)
        
        assert response.status_code == 200
        content_disposition = response['Content-Disposition']
        
        # Check filename format: device-{hostname}-{timestamp}.pdf
        assert 'filename=' in content_disposition
        filename = content_disposition.split('filename=')[1].strip('"')
        assert filename.startswith('device-')
        assert filename.endswith('.pdf')
        assert 'test-server' in filename  # hostname from sample_lynis_report

    def test_export_pdf_no_report(self, test_user, test_device):
        """Test exporting PDF for device with no report returns 404."""
        client = Client()
        client.force_login(test_user)
        
        url = reverse('device_export_pdf', kwargs={'device_id': test_device.id})
        response = client.get(url)
        
        assert response.status_code == 404
        assert response.content == b'No report found for the device'

    def test_export_pdf_invalid_device_id(self, test_user):
        """Test exporting PDF with invalid device ID returns 404."""
        client = Client()
        client.force_login(test_user)
        
        url = reverse('device_export_pdf', kwargs={'device_id': 99999})
        response = client.get(url)
        
        assert response.status_code == 404

    def test_export_pdf_unauthorized(self, test_device, sample_lynis_report):
        """Test unauthenticated user cannot export PDF."""
        client = Client()
        
        # Create a full report for the device
        FullReport.objects.create(
            device=test_device,
            full_report=sample_lynis_report
        )
        
        url = reverse('device_export_pdf', kwargs={'device_id': test_device.id})
        response = client.get(url)
        
        # Should redirect to login page
        assert response.status_code == 302
        assert '/login' in response.url

    def test_export_pdf_content_includes_device_info(self, test_user, test_device, sample_lynis_report):
        """Test PDF content includes device information."""
        client = Client()
        client.force_login(test_user)
        
        # Create a full report for the device
        FullReport.objects.create(
            device=test_device,
            full_report=sample_lynis_report
        )
        
        url = reverse('device_export_pdf', kwargs={'device_id': test_device.id})
        response = client.get(url)
        
        assert response.status_code == 200
        
        # PDF is binary, but we can check it's not empty and has PDF header
        assert len(response.content) > 0
        # PDF files start with %PDF
        assert response.content.startswith(b'%PDF')

    def test_export_pdf_invalid_report_data(self, test_user, test_device):
        """Test exporting PDF with invalid report data returns 500."""
        client = Client()
        client.force_login(test_user)
        
        # Create a report with invalid data that can't be parsed
        FullReport.objects.create(
            device=test_device,
            full_report='Invalid report data that cannot be parsed'
        )
        
        url = reverse('device_export_pdf', kwargs={'device_id': test_device.id})
        response = client.get(url)
        
        # Should return 500 if report parsing fails
        assert response.status_code == 500
        assert response.content == b'Failed to parse the report'


@pytest.mark.django_db
class TestUserProfileView:
    """Tests for the profile management view."""

    def test_profile_page_renders(self, test_user):
        client = Client()
        client.force_login(test_user)

        response = client.get(reverse('profile'))

        assert response.status_code == 200
        assert b'Your Profile' in response.content
        assert b'Profile information' in response.content
        assert b'Password' in response.content
        assert b"Your password can\xe2\x80\x99t be too similar" not in response.content

    def test_profile_information_update(self, test_user):
        client = Client()
        client.force_login(test_user)

        payload = {
            'form_type': 'profile',
            'username': test_user.username,
            'first_name': 'Alice',
            'last_name': 'Admin',
            'email': 'alice.admin@example.com',
        }

        response = client.post(reverse('profile'), data=payload, follow=True)

        assert response.status_code == 200
        test_user.refresh_from_db()
        assert test_user.first_name == 'Alice'
        assert test_user.last_name == 'Admin'
        assert test_user.email == 'alice.admin@example.com'

    def test_profile_email_uniqueness_validation(self, test_user):
        other_user = User.objects.create_user(
            username='existing_user',
            email='taken@example.com',
            password='Secretpass123'
        )
        client = Client()
        client.force_login(test_user)

        payload = {
            'form_type': 'profile',
            'username': test_user.username,
            'first_name': 'Bob',
            'last_name': 'Builder',
            'email': other_user.email,
        }

        response = client.post(reverse('profile'), data=payload)

        assert response.status_code == 200
        assert b'This email address is already being used by another account.' in response.content

    def test_password_change_flow(self, test_user):
        test_user.set_password('OldP@ssw0rd!')
        test_user.save()

        client = Client()
        assert client.login(username=test_user.username, password='OldP@ssw0rd!')

        payload = {
            'form_type': 'password',
            'old_password': 'OldP@ssw0rd!',
            'new_password1': 'N3wP@ssw0rd!',
            'new_password2': 'N3wP@ssw0rd!',
        }

        response = client.post(reverse('profile'), data=payload, follow=True)

        assert response.status_code == 200
        test_user.refresh_from_db()
        assert test_user.check_password('N3wP@ssw0rd!')

        client.logout()
        assert client.login(username=test_user.username, password='N3wP@ssw0rd!')
        assert not client.login(username=test_user.username, password='OldP@ssw0rd!')

    def test_password_change_allows_name_similarity(self, test_user):
        test_user.first_name = 'Alice'
        test_user.set_password('OldP@ssw0rd!')
        test_user.save()

        client = Client()
        assert client.login(username=test_user.username, password='OldP@ssw0rd!')

        payload = {
            'form_type': 'password',
            'old_password': 'OldP@ssw0rd!',
            'new_password1': 'Alice1234!',
            'new_password2': 'Alice1234!',
        }

        response = client.post(reverse('profile'), data=payload, follow=True)

        assert response.status_code == 200
        test_user.refresh_from_db()
        assert test_user.check_password('Alice1234!')


@pytest.mark.django_db
class TestRuleDetailView:
    """Tests for the rule_detail endpoint."""

    def test_rule_detail_page_renders(self, test_user):
        """Test that rule detail page renders successfully."""
        from api.models import PolicyRule
        
        # Create a test rule
        rule = PolicyRule.objects.create(
            name='Test Rule',
            description='Test description',
            rule_query='test_query',
            enabled=True,
            created_by=test_user,
            is_system=False
        )
        
        client = Client()
        client.force_login(test_user)
        
        url = reverse('rule_detail', kwargs={'rule_id': rule.id})
        response = client.get(url)
        
        assert response.status_code == 200
        assert b'Test Rule' in response.content
        assert b'Test description' in response.content
        assert b'test_query' in response.content

    def test_rule_detail_with_system_rule(self, test_user):
        """Test that system rule detail page renders correctly."""
        from api.models import PolicyRule
        from django.contrib.auth.models import User
        
        # Get or create system user
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={'is_active': False, 'is_staff': False, 'is_superuser': False}
        )
        
        # Create a system rule
        rule = PolicyRule.objects.create(
            name='System Rule',
            description='System rule description',
            rule_query='system_query',
            enabled=True,
            created_by=system_user,
            is_system=True
        )
        
        client = Client()
        client.force_login(test_user)
        
        url = reverse('rule_detail', kwargs={'rule_id': rule.id})
        response = client.get(url)
        
        assert response.status_code == 200
        assert b'System Rule' in response.content
        assert b'System' in response.content  # Should show "System" as creator

    def test_rule_detail_invalid_id(self, test_user):
        """Test rule detail with invalid ID returns 404."""
        client = Client()
        client.force_login(test_user)
        
        url = reverse('rule_detail', kwargs={'rule_id': 99999})
        response = client.get(url)
        
        assert response.status_code == 404

    def test_rule_detail_unauthorized(self):
        """Test unauthenticated user cannot access rule detail."""
        from api.models import PolicyRule
        from django.contrib.auth.models import User
        
        test_user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        rule = PolicyRule.objects.create(
            name='Test Rule',
            description='Test',
            rule_query='test',
            created_by=test_user
        )
        
        client = Client()
        
        url = reverse('rule_detail', kwargs={'rule_id': rule.id})
        response = client.get(url)
        
        # Should redirect to login page
        assert response.status_code == 302
        assert '/login' in response.url
