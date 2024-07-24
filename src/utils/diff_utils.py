import difflib
import logging

def generate_diff(old_report, new_report):        
    diff = difflib.unified_diff(
        old_report.splitlines(keepends=True), 
        new_report.splitlines(keepends=True), 
        lineterm=''
    )
    return ''.join(diff)

def apply_diff(original, diff):
    logging.debug('Original report size: %d bytes', len(original))
    logging.debug('Diff size: %d bytes', len(diff))

    original_lines = original.splitlines(keepends=True)
    diff_lines = diff.splitlines(keepends=True)

    # Combine original lines and diff lines
    full_diff = list(difflib.unified_diff(original_lines, original_lines)) + diff_lines

    # Apply the full diff to reconstruct the report
    patched_lines = list(difflib.restore(full_diff, 1))
    return ''.join(patched_lines)

def parse_diff(diff):
    changes = {
        'added': [],
        'removed': []
    }

    diff_lines = diff.splitlines(keepends=True)
    for line in diff_lines:
        if line.startswith('+++') or line.startswith('@@') or line.startswith('---'):
            continue
        if line.startswith('+'):
            changes['added'].append(line[1:])
        elif line.startswith('-'):
            changes['removed'].append(line[1:])

    return changes

def compare_delimited_values(old_value, new_value, delimiter='|'):
    old_items = set(old_value.split(delimiter))
    new_items = set(new_value.split(delimiter))
    added_items = new_items - old_items
    removed_items = old_items - new_items
    return list(added_items), list(removed_items)

def filter_diff(diff):
    """ Remove some items from the diff """
    ignore_keys = [
        'report_datetime_start',
        'report_datetime_end',
        'slow_test',
        'uptime_in_seconds'
    ]

    diff_lines = diff.splitlines(keepends=True)
    filtered_diff = []
    for line in diff_lines:
        if not any(key in line for key in ignore_keys):
            filtered_diff.append(line)
    return ''.join(filtered_diff)

def analyze_diff(diff):
    changes = parse_diff(diff)
    change_details = {
        'added': [],
        'removed': [],
        'changed': [],
    }

    added_dict = {line.split('=')[0].strip(): line.split('=', 1)[1].strip() for line in changes['added'] if '=' in line}
    removed_dict = {line.split('=')[0].strip(): line.split('=', 1)[1].strip() for line in changes['removed'] if '=' in line}

    # Detect added and removed fields
    for key in added_dict:
        if key in removed_dict:
            old_value = removed_dict[key]
            new_value = added_dict[key]
            
            if old_value != new_value:
                if "|" in old_value or "|" in new_value:
                    added_items, removed_items = compare_delimited_values(old_value, new_value)
                    change_details['changed'].append((key, 'added_items', added_items))
                    change_details['changed'].append((key, 'removed_items', removed_items))
                else:
                    change_details['changed'].append((key, old_value, new_value))
        else:
            change_details['added'].append({key: added_dict[key]})
    
    for key in removed_dict:
        if key not in added_dict:
            change_details['removed'].append({key: removed_dict[key]})
    
    return change_details