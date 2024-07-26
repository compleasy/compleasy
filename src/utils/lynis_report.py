import os
import logging

class LynisReport:
    def __init__(self, full_report):
        self.keys = {}
        self.report = full_report
        self.report = self.clean_full_report()
        self.keys = self.parse_report()

    def clean_full_report(self):
        """Clean invalid keys from the report"""
        invalid_tests = [
            'DEB-0280',
            'DEB-0285',
            'DEB-0520',
            'DEB-0870',
            'DEB-0880'
        ]

        # Remove lines with invalid tests
        report_lines = self.report.split('\n')
        for line in report_lines:
            for test in invalid_tests:
                if test in line:
                    report_lines.remove(line)
                    break
        return '\n'.join(report_lines)

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

        # Check if key is a list
        if not self.is_key_list(key):
            # Is not a list
            # key = value
            return self.keys.get(key)
        
        logging.debug('Key is a list: %s', key)

        # It is a list
        values = self.keys.get(key, [])

        parsed_values = []
        for value in values:
            parsed_values.append(self.parse_value_list(value))

        # Parse the value
        return parsed_values
        
        