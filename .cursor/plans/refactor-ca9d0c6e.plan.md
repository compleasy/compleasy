<!-- ca9d0c6e-0d50-4a61-9efe-4d94a7364eec fd0fca66-79ee-4143-b5cb-842bbe9b0a26 -->
# Refactor Report Diff System to Object-Based Comparison

## Overview

Replace the current text-based diff system (using `difflib.unified_diff`) with direct object comparison of parsed report dictionaries. Store structured changes as JSON and move ignore patterns to database with per-organization configuration.

## Database Changes

### 1. Create ActivityIgnorePattern Model

Create new model in `src/api/models.py`:

- `organization` ForeignKey (relates to Organization)
- `pattern` CharField (the key pattern to ignore, e.g., `report_datetime_start`)
- `is_active` BooleanField (allow temporary disable)
- `created_at`, `updated_at` DateTimeFields

### 2. Migrate DiffReport.diff_report Field

Change `DiffReport.diff_report` from TextField to JSONField:

- Migration will convert existing text diffs to empty JSON `{}` (acceptable since no backward compatibility needed)
- New structure: `{'added': {...}, 'removed': {...}, 'changed': [...]}`

## Code Changes

### 3. Add compare_reports() Method to LynisReport

Create new method in `src/api/utils/lynis_report.py`:

```python
def compare_reports(self, new_report_str: str, ignore_keys: List[str] = []) -> Dict[str, Any]:
    """Compare current report with new report, return structured changes."""
    new_report = LynisReport(new_report_str)
    old_keys = self.keys
    new_keys = new_report.keys
    
    changes = {'added': {}, 'removed': {}, 'changed': []}
    
    all_keys = set(old_keys.keys()) | set(new_keys.keys())
    
    for key in all_keys:
        if key in ignore_keys:
            continue
            
        old_val = old_keys.get(key)
        new_val = new_keys.get(key)
        
        if old_val is None and new_val is not None:
            changes['added'][key] = new_val
        elif old_val is not None and new_val is None:
            changes['removed'][key] = old_val
        elif old_val != new_val:
            changes['changed'].append({key: {'old': old_val, 'new': new_val}})
    
    return changes
```

### 4. Remove LynisReport.Diff Class

Delete the entire `LynisReport.Diff` class and `diff()` method from `src/api/utils/lynis_report.py` as they are no longer needed.

### 5. Update upload_report() in api/views.py

Replace lines 79-90 with new comparison logic:

```python
if latest_full_report:
    try:
        latest_lynis = LynisReport(latest_full_report.full_report)
        # Get ignore patterns for device's organization
        org = device.licensekey.organization
        ignore_keys = list(ActivityIgnorePattern.objects.filter(
            organization=org, is_active=True
        ).values_list('pattern', flat=True))
        
        # Generate structured diff
        diff_data = latest_lynis.compare_reports(report_data, ignore_keys)
        DiffReport.objects.create(device=device, diff_report=diff_data)
        logging.info(f'Diff created for device {post_hostid}')
        logging.debug('Changed items: %s', diff_data)
    except DatabaseError as e:
        logging.error(f'Database error creating diff report: {e}')
        return internal_error('Database error while creating diff report')
```

### 6. Update activity() in frontend/views.py

Replace lines 1000-1077 with direct JSON access:

- Remove `LynisReport.Diff` instantiation (line 1035)
- Remove `lynis_diff.analyze()` call (line 1037)
- Access `diff_report.diff_report` directly as dict (it's already parsed JSON)
- Remove hardcoded `ignore_keys` list (lines 1019-1033) as filtering now happens at creation time
```python
for diff_report in diff_reports:
    if len(activities) >= max_activities:
        break
    
    diff_data = diff_report.diff_report  # Already a dict from JSONField
    
    if 'added' in diff_data and 'removed' in diff_data:
        for change_type in ['added', 'removed']:
            for key, values in diff_data[change_type].items():
                # Normalize to list
                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    activities.append({
                        'device': diff_report.device,
                        'created_at': diff_report.created_at,
                        'key': key,
                        'value': value,
                        'type': change_type
                    })
    
    if 'changed' in diff_data:
        for change in diff_data['changed']:
            key = list(change.keys())[0]
            activities.append({
                'device': diff_report.device,
                'created_at': diff_report.created_at,
                'key': key,
                'old_value': change[key]['old'],
                'new_value': change[key]['new'],
                'type': 'changed'
            })
```


## Migration

### 7. Create Data Migration

Create migration `src/api/migrations/0011_refactor_diff_system.py`:

1. Add `ActivityIgnorePattern` model
2. Convert `DiffReport.diff_report` to JSONField
3. Populate default ignore patterns for all existing organizations:

   - `report_datetime_start`, `report_datetime_end`
   - `slow_test`, `uptime_in_seconds`, `uptime_in_days`
   - `deleted_file`, `lynis_timer_next_trigger`
   - `clamav_last_update`, `tests_executed`, `tests_skipped`
   - `installed_packages_array`, `vulnerable_package`, `suggestion`

## Testing

### 8. Update Tests

- Update `src/api/tests.py`: Remove tests for `LynisReport.Diff` class
- Update `src/frontend/tests.py`: 
  - Remove `monkeypatch.setattr(LynisReport.Diff, 'analyze', ...)` calls
  - Mock `diff_report.diff_report` as dict instead of text
  - Update `test_activity_view_*` tests to use JSON structure
- Add new test for `compare_reports()` method
- Add new test for `ActivityIgnorePattern` model

## Benefits

- Faster: No text diff generation/parsing overhead
- Type-safe: Preserves data types (int, str, list) throughout pipeline
- Cleaner code: Direct dict access, no parsing
- Configurable: Per-org ignore patterns via database
- Foundation for future features: Easy to add notification rules, custom filters

### To-dos

- [ ] Create ActivityIgnorePattern model in api/models.py
- [ ] Add compare_reports() method to LynisReport class
- [ ] Remove LynisReport.Diff class and diff() method
- [ ] Update upload_report() to use object comparison
- [ ] Update activity() to read JSON directly
- [ ] Create migration for JSONField and default ignore patterns
- [ ] Update all tests to work with new diff structure
- [ ] Run full test suite and verify Lynis integration