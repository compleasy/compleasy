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
    
    def get_server_role(self):
        """Try to determine the server role based on the listening ports."""

        port_role = {
            '25': 'Mail server',
            '80': 'Web server',
            '443': 'Web server',
            '110': 'Mail server',
            '143': 'Mail server',
            '587': 'Mail server',
            '3306': 'Database server',
            '8006': 'ProxmoxVE',
            '8007': 'ProxmoxBS'
        }

        # If the server is listening on ports 80 or 443, it's probably a web server
        network_listen_ports = self.keys.get('network_listen', [])
        for listen_port in network_listen_ports:
            for port, role in port_role.items():
                if port in listen_port:
                    # Determine the application based on the port (last part of the string)
                    parts = listen_port.split('|')
                    # Remove empty parts (part is empty or contains just a -)
                    parts = [part for part in parts if part and part != '-']
                    if parts:
                        application = parts[-1]
                    return f'{role} ({application})'
        return 'unknown'

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
        
        # Determine the server role
        parsed_keys['server_role'] = self.get_server_role()

        # Optionally, you can count the warnings and suggestions if needed
        parsed_keys['count_warnings'] = len(parsed_keys.get('warning', []))
        parsed_keys['count_suggestions'] = len(parsed_keys.get('suggestion', []))
        
        return parsed_keys
    
    def get(self, key):
        """Get the value of a specific key."""
        return self.keys.get(key)