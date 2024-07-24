import os
import logging

class LynisReport:
    def __init__(self, full_report):
        self.keys = {}
        self.report = full_report
        self.keys = self.parse_report()

    def get_full_report(self):
        """Return the full report content."""
        return self.report

    def parse_report(self):
        """Parse the report and count warnings and suggestions."""
        parsed_keys = {}
        
        for line in self.report.split('\n'):
            if not line or line.startswith('#') or '=' not in line:
                continue
            
            key, value = line.split('=', 1)
            
            # Check if the key indicates a list type (contains '[]')
            if '[]' in key:
                base_key = key.replace('[]', '')
                if base_key not in parsed_keys:
                    parsed_keys[base_key] = []
                parsed_keys[base_key].append(value)
            else:
                parsed_keys[key] = value
        
        # Optionally, you can count the warnings and suggestions if needed
        parsed_keys['count_warnings'] = len(parsed_keys.get('warning', []))
        parsed_keys['count_suggestions'] = len(parsed_keys.get('suggestion', []))
        
        return parsed_keys
    
    def get(self, key):
        """Get the value of a specific key."""
        return self.keys.get(key)
    
    def diff(self, other_report):
        """
        Compare two reports and return the differences.
        Ignore some keys that are not relevant for the comparison.
        Take into account some keys are lists, so we need to compare them differently.
        The dict contains a key "change" with the following values: added, removed, changed
        """
        keys_to_ignore = ['report_datetime_start', 'report_datetime_end', 'slow_test', 'uptime_in_seconds','count_warnings', 'count_suggestions']

        diff = {
            'added': {},
            'removed': {},
            'changed': {}
        }

        for key, value in self.keys.items():
            # Ignore some keys
            if key in keys_to_ignore:
                continue

            # if the key is a list, compare the lists and store only the differences
            if isinstance(value, list):
                if key in other_report.keys and value != other_report.keys[key]:
                    # Compare the lists and store the differences. Avoid empty values
                    added_values = list(set(value) - set(other_report.keys[key]))
                    if added_values:
                        diff['added'][key] = added_values
                    
                    removed_values = list(set(other_report.keys[key]) - set(value))
                    if removed_values:
                        diff['removed'][key] = removed_values

            else:
                if key in other_report.keys and value != other_report.keys[key]:
                    # IF the value has | as separator, split it and store only the differences
                    if '|' in value:
                        # Split the value and compare the lists. Avoid empty values
                        diff['changed'][key] = list(set(value.split('|')) - set(other_report.keys[key].split('|')))
                    else:
                        diff['changed'][key] = value
                elif key not in other_report.keys:
                    diff['removed'][key] = value
                elif key not in self.keys:
                    diff['added'][key] = value
                    
        return diff