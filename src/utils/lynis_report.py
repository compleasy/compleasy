import os

class LynisReport:
    def __init__(self, report_file_or_content):
        self.keys = {}
        self.report = self.read_report(report_file_or_content)
        self.keys = self.parse_report()

    def read_report(self, report_file_or_content):
        """Read the report from a file or direct content."""
        if os.path.exists(report_file_or_content):
            with open(report_file_or_content, 'r') as file:
                return file.read()
        return report_file_or_content

    def get_full_report(self):
        """Return the full report content."""
        return self.report

    def parse_report(self):
        """Parse the report and count warnings and suggestions."""
        warning_count = 0
        suggestion_count = 0
        parsed_keys = {}
        
        for line in self.report.split('\n'):
            if not line or line.startswith('#') or '=' not in line:
                continue
            
            key, value = line.split('=', 1)
            if key == 'warning[]':
                warning_count += 1
            elif key == 'suggestion[]':
                suggestion_count += 1
            
            parsed_keys[key] = value

        parsed_keys['count_warnings'] = warning_count
        parsed_keys['count_suggestions'] = suggestion_count
        
        return parsed_keys
    
    def get(self, key):
        """Get the value of a specific key."""
        return self.keys.get(key)
