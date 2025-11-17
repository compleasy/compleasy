# Lynis License Key Format Compliance

## Overview

Lynis clients filter license keys to only allow hexadecimal characters and hyphens using the filter `[a-f0-9-]`. This document confirms that TrikuSec's license key generation complies with this requirement.

## Lynis License Key Validation

According to the Lynis code, license keys are validated using the following bash command:

```bash
echo "${LICENSE_KEY}" | ${TRBINARY} -cd '[a-f0-9-]'
```

This means Lynis **only accepts** license keys containing:
- Lowercase hexadecimal characters: `a-f`
- Digits: `0-9`
- Hyphens: `-`

Any other characters (uppercase letters, special characters, etc.) will be stripped out.

## TrikuSec Implementation

TrikuSec's license key generation is **fully compliant** with Lynis's format requirement.

### Implementation Details

**Location**: `src/api/utils/license_utils.py`

**Function**: `generate_license_key()`

```python
def generate_license_key():
    """
    Generate a unique license key in format: xxxxxxxx-xxxxxxxx-xxxxxxxx
    Uses lowercase hex characters (a-f0-9) to match existing format.
    
    Returns:
        str: A unique license key string
    """
    characters = 'abcdef0123456789'
    
    # Generate until we find a unique key
    max_attempts = 100
    for _ in range(max_attempts):
        license_key = (
            ''.join(random.choices(characters, k=8))
            + '-'
            + ''.join(random.choices(characters, k=8))
            + '-'
            + ''.join(random.choices(characters, k=8))
        )
        
        # Check if key already exists
        if not LicenseKey.objects.filter(licensekey=license_key).exists():
            return license_key
    
    raise ValueError("Unable to generate unique license key after multiple attempts")
```

### Key Format

- **Characters**: Only lowercase hexadecimal (`a-f`, `0-9`)
- **Separators**: Hyphens (`-`)
- **Format**: `xxxxxxxx-xxxxxxxx-xxxxxxxx` (3 segments of 8 hex characters)
- **Total Length**: 26 characters (24 hex + 2 hyphens)

### Example Keys

```
a1b2c3d4-e5f6a7b8-c9d0e1f2
00112233-44556677-8899aabb
deadbeef-cafebabe-feedface
```

## Test Coverage

The compliance is verified by automated tests in `src/api/tests.py`:

### Test: `test_generate_license_key_format_lynis_compatible`

This test generates 10 license keys and verifies each one:

1. ✅ Has correct length (26 characters)
2. ✅ Has exactly 2 hyphens
3. ✅ Only contains hexadecimal characters `[a-f0-9]` and hyphens
4. ✅ Is lowercase (no uppercase letters)
5. ✅ Has 3 parts of 8 characters each

**Test command**:
```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test \
  pytest api/tests.py::TestLicenseValidation::test_generate_license_key_format_lynis_compatible -v
```

**Result**: ✅ **PASSED** - All generated keys comply with Lynis format

## Compatibility Guarantee

TrikuSec **guarantees** that all generated license keys will:

1. Work with Lynis clients without modification
2. Pass Lynis's `tr -cd '[a-f0-9-]'` filter unchanged
3. Contain only characters from the set `[a-f0-9-]`
4. Follow the format `xxxxxxxx-xxxxxxxx-xxxxxxxx`

## Important Notes

### Do NOT Change the Character Set

The character set in `generate_license_key()` must remain:

```python
characters = 'abcdef0123456789'  # DO NOT CHANGE
```

**Never** add:
- Uppercase letters (A-Z, G-Z)
- Special characters (!, @, #, $, etc.)
- Whitespace
- Additional digits beyond 0-9
- Additional letters beyond a-f

### Why Lowercase Only?

While uppercase hexadecimal characters (A-F) are technically valid hex, we use **lowercase only** for consistency and to avoid case-sensitivity issues in:

- Database queries
- User copy/paste operations
- Log file analysis
- URL parameters

## Verification

If you modify the license key generation algorithm, **always** run the compliance test:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test \
  pytest api/tests.py::TestLicenseValidation -v
```

This ensures:
- Keys are unique
- Format is correct
- Lynis compatibility is maintained
- All license validation functions work correctly

## References

- TrikuSec License Utils: `src/api/utils/license_utils.py`
- TrikuSec Tests: `src/api/tests.py::TestLicenseValidation`
- Lynis Documentation: https://cisofy.com/lynis/

