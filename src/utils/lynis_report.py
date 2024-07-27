import os
import logging

class LynisReport:
    def __init__(self, full_report):
        self.keys = {}
        self.report = full_report
        self.report = self.clean_full_report()
        self.keys = self.parse_report()
        # Generate count variables for lists
        # Example: warning_count, suggestion_count, vulnerable_package_count
        self.generate_count_variables()

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
        
        return parsed_keys
    
    def get_parsed_report(self):
        """Return the parsed report."""
        return self.keys

    def generate_count_variables(self):
        """Generate count variables for lists."""
        
        count_keys = {}
        for key, value in self.keys.items():
            if isinstance(value, list):
                count_keys[f'{key}_count'] = len(value)
                logging.debug(f'Generated count key: {key}_count with value: {len(value)}')
        self.keys.update(count_keys)
    
    def get(self, key):
        """Get the value of a specific key."""
        return self.keys.get(key)
        
        