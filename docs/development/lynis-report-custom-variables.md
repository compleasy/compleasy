# Lynis Report Parsing & Custom Variables

This document explains how TrikuSec ingests raw Lynis reports and where custom, dynamically generated fields (such as `days_since_audit`) are created.

## Parsing Workflow

1. **Upload**  
   The Lynis client posts raw report text to `/api/lynis/upload/`. The payload is stored verbatim in `FullReport.full_report`.

2. **On-Demand Parsing**  
   Views, policy evaluation utilities, and reporting helpers instantiate `api.utils.lynis_report.LynisReport` with the stored text whenever structured access is needed.

3. **Base Keys**  
   `LynisReport` converts the Lynis key/value format into a Python dictionary (`self.keys`).  
   * Scalar strings are preserved.  
   * Numeric strings are cast to integers for reliable comparisons.  
   * Keys with the `[]` suffix become lists.  

4. **Custom Variable Generation**  
   After parsing, `_generate_custom_variables()` enriches the dictionary with derived values. All callers automatically see these values via `get_parsed_report()`.

## Existing Custom Variables

| Key | Description | Source |
| --- | --- | --- |
| `<list>_count` | Number of elements for any list-type key | `_generate_count_variables()` |
| `primary_ipv4_addresses` | IPv4 addresses that share a /24 with the default gateway(s) | `_get_filtered_ipv4_addresses()` |
| `days_since_audit` | Whole days elapsed since the last `report_datetime_end` | `_add_days_since_audit_variable()` |

### `days_since_audit`

* Calculated every time a report is parsed.  
* Accepts both `"YYYY-MM-DD HH:MM:SS"` and ISO-8601 strings (with `T` separator and optional offset).  
* Uses `django.utils.timezone.now()` to keep values timezone-aware.  
* Negative differences (future timestamps / clock skew) clamp to `0`.  
* Exposed to policy queries, templates, PDFs, and exported JSON via `report['days_since_audit']`.

## Adding New Custom Fields

1. Open `src/api/utils/lynis_report.py`.  
2. Extend `_generate_custom_variables()` to call a new helper, or reuse existing ones.  
3. Use `self.get()` to pull existing parsed values; use `self.set()` to store derived ones.  
4. Prefer pure functions without I/O: the parser runs in request/response paths and should remain fast.  
5. Add unit tests under `src/api/tests.py` (see `TestLynisReportCustomVariables`).  
6. Update documentation and any policy examples that rely on the new field.

Following this pattern keeps all derived data centralized, avoiding schema migrations while still making new computed fields immediately available across the platform.

