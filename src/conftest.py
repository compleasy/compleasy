import pytest
from django.contrib.auth.models import User
from api.models import LicenseKey, Device, FullReport, DiffReport
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = Faker('user_name')
    email = Faker('email')
    password = Faker('password')


class LicenseKeyFactory(DjangoModelFactory):
    class Meta:
        model = LicenseKey
        django_get_or_create = ('licensekey',)

    licensekey = Faker('uuid4')
    created_by = SubFactory(UserFactory)


class DeviceFactory(DjangoModelFactory):
    class Meta:
        model = Device

    licensekey = SubFactory(LicenseKeyFactory)
    hostid = Faker('uuid4')
    hostid2 = Faker('uuid4')
    hostname = Faker('hostname')
    os = 'Linux'
    distro = 'Ubuntu'
    distro_version = '22.04'
    lynis_version = '3.0.0'
    warnings = 0
    compliant = True


@pytest.fixture
def test_user(db):
    """Create a test user."""
    return UserFactory()


@pytest.fixture
def test_license_key(db, test_user):
    """Create a test license key."""
    return LicenseKeyFactory(created_by=test_user, licensekey='test-license-key-123')


@pytest.fixture
def test_device(db, test_license_key):
    """Create a test device."""
    return DeviceFactory(
        licensekey=test_license_key,
        hostid='test-host-id-1',
        hostid2='test-host-id-2'
    )


@pytest.fixture
def sample_lynis_report():
    """Sample Lynis report data for testing."""
    return """# Lynis Report
report_version_major=1
report_version_minor=0
report_datetime_start=2024-01-01T10:00:00
report_datetime_end=2024-01-01T10:05:00
hostname=test-server
os=Linux
os_fullname=Ubuntu
os_version=22.04
lynis_version=3.0.0
warning_count=5
suggestion_count=10
test_skip_always=CRYP-7902
kernel_version=5.15.0
boot_mode=UEFI
hardening_index=65
"""


@pytest.fixture
def sample_lynis_report_updated():
    """Updated sample Lynis report data for testing diff generation."""
    return """# Lynis Report
report_version_major=1
report_version_minor=0
report_datetime_start=2024-01-01T11:00:00
report_datetime_end=2024-01-01T11:05:00
hostname=test-server
os=Linux
os_fullname=Ubuntu
os_version=22.04
lynis_version=3.0.1
warning_count=3
suggestion_count=8
test_skip_always=CRYP-7902
kernel_version=5.15.0
boot_mode=UEFI
hardening_index=70
"""


@pytest.fixture
def sample_lynis_report_minimal():
    """Minimal Lynis report data for basic testing."""
    return """# Lynis Report
report_version_major=1
report_version_minor=0
hostname=minimal-test
os=Linux
lynis_version=3.0.0
"""

