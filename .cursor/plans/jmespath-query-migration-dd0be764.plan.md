<!-- dd0be764-f328-4b94-9755-839edbd1f9e6 87709f73-40c2-4a74-83cb-d0d1b9ab7691 -->
# Migrate Policy Query System to JMESPath

## Overview

Replace custom pyparsing query implementation with JMESPath to support complex boolean expressions while maintaining security and simplicity.

## Changes Required

### 1. Dependencies

**File**: `src/requirements.txt`

- Add `jmespath>=1.0.1` to dependencies
- Remove `pyparsing` dependency (if not used elsewhere)

### 2. Core Query Logic

**File**: `src/api/utils/policy_query.py`

- Replace entire file with JMESPath implementation
- Remove `parse_query()` function (JMESPath has built-in parsing)
- Rewrite `evaluate_query()` to use `jmespath.compile()` and `.search()`
- Handle JMESPath exceptions gracefully
- Return `True`/`False`/`None` as before

**Key implementation**:

```python
import jmespath
import logging

def evaluate_query(report, query):
    """Evaluate a JMESPath query against a report."""
    try:
        expression = jmespath.compile(query)
        result = expression.search(report)
        # JMESPath returns the query result; convert to boolean
        if isinstance(result, bool):
            return result
        return bool(result)
    except jmespath.exceptions.JMESPathError as e:
        logging.error(f'Invalid JMESPath query: {e}')
        return None
```

### 3. View Updates

**File**: `src/frontend/views.py`

- Remove `parse_query()` import (line 11)
- Remove `parsed_query = parse_query(rule.rule_query)` logic (line 674)
- Remove query parsing validation in `rule_evaluate_for_device()` (lines 674-685)
- Simplify to just call `rule.evaluate(parsed_report)` directly

**Reason**: JMESPath handles parsing internally; no need for separate parse step

### 4. Security Tests

**File**: `src/api/tests_policy_security.py`

- Update sample report fixture to use proper JMESPath syntax
- Remove `parse_query()` import and related tests
- Update SQL injection tests (JMESPath doesn't parse SQL syntax differently)
- Update code injection tests (JMESPath already sandboxed)
- Update operator validation tests with JMESPath operators
- Keep resource exhaustion test (verify JMESPath handles long queries)

**Test queries need updating**:

- Old: `hardening_index > 70` → New: `hardening_index > \`70\``
- Old: `automation_tool_running contains "ansible"` → New: `contains(automation_tool_running, 'ansible')`

### 5. Documentation

**File**: `docs/usage/policies.md`

- Update "Rule Query Syntax" section (lines 34-87)
- Replace custom syntax with JMESPath syntax guide
- Update operators list (use JMESPath operators)
- Add AND/OR/NOT examples
- Update all query examples throughout the document
- Add link to JMESPath documentation for advanced users

**New syntax examples**:

```
# Simple comparisons
os == 'Linux'
hardening_index > `70`
hardening_index >= `60`

# Contains (built-in function)
contains(automation_tool_running, 'ansible')

# Complex boolean logic (NEW!)
os == 'Linux' && hardening_index > `70`
hardening_index < `50` || vulnerable_packages_found > `0`
!(firewall_active == `1`)
```

### 6. UI Form Help Text

**File**: `src/frontend/templates/policy/rule_edit_sidebar.html`

- Update help text (line 39) with JMESPath syntax hint
- Add example: `os == 'Linux' && hardening_index > \`70\``

**File**: `src/frontend/forms.py`

- Update placeholder text (line 60) with JMESPath example

### 7. Agent Guidelines

**File**: `.cursor/rules.md` (Agent Guidelines)

- Update Rule Query Syntax section with JMESPath reference
- Note that complex queries are now supported
- Add warning about 255 char limit for queries

## Testing Strategy

1. **Run security tests**: Verify JMESPath doesn't introduce vulnerabilities
2. **Test simple queries**: `hardening_index > \`70\``
3. **Test complex queries**: `os == 'Linux' && hardening_index > \`70\``
4. **Test contains**: `contains(automation_tool_running, 'ansible')`
5. **Test missing fields**: Verify graceful handling
6. **Test invalid syntax**: Verify error messages are clear

## Syntax Migration Reference

| Old Syntax | New JMESPath Syntax |

|------------|---------------------|

| `field = "value"` | `field == 'value'` |

| `field != "value"` | `field != 'value'` |

| `field > 70` | `field > \`70\`` |

| `field >= 70` | `field >= \`70\`` |

| `field < 70` | `field < \`70\`` |

| `field <= 70` | `field <= \`70\`` |

| `field contains "value"` | `contains(field, 'value')` |

| *(not supported)* | `field1 == 'x' && field2 > \`5\`` |

| *(not supported)* | `field1 == 'x' \|\| field2 == 'y'` |

| *(not supported)* | `!(field == \`1\`)` |

## Notes

- No database migration needed (still storing query strings)
- No existing production rules to convert
- 255 char limit enforced for simplicity
- JMESPath is sandboxed (no code execution risk)
- Backward compatibility: Not needed (fresh start)

### To-dos

- [ ] Add jmespath>=1.0.1 to src/requirements.txt
- [ ] Rewrite src/api/utils/policy_query.py to use JMESPath instead of pyparsing
- [ ] Update src/frontend/views.py to remove parse_query() usage and simplify validation
- [ ] Update src/api/tests_policy_security.py with JMESPath syntax and remove parse_query tests
- [ ] Update docs/usage/policies.md with JMESPath syntax guide and examples
- [ ] Update form help text and placeholders in templates and forms.py
- [ ] Update .cursor/rules.md with JMESPath reference
- [ ] Run all tests to verify migration works correctly