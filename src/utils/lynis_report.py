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
        roles = []
        network_listen_ports = self.get('network_listen')
        logging.debug('Network listen ports: %s', network_listen_ports)
        if not network_listen_ports:
            return ['unknown']
        
        for listening_port in network_listen_ports:
            address_port = listening_port[2]
            application = listening_port[-1]
            for port, role in port_role.items():
                if address_port.endswith(port):
                    roles.append(f'{role} ({application})')
        
        if not roles:
            return ['unknown']
        
        return roles

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
    
    def is_list(self, key):
        """Check if the exists and is a list."""
        value = self.keys.get(key)
        return isinstance(value, list)
    
    def parse_value(self, value):
        """Parse the value of a key."""
        if not value:
            return ''
        
        if not '|' in value:
            # key=value
            logging.debug('Value is not a list: %s', value)
            return value
        
        logging.debug('Value is a list: %s', value)
        
        # If the value contains multiple parts, split it by '|'
        value_parts = value.split('|')
        # Remove empty parts (part is empty or contains just a -)
        value_parts = [part for part in value_parts if part and part != '-']

        return value_parts

    def get(self, key):
        """Get the value of a specific key."""

        # Check if is a list
        if not self.is_list(key):
            # Is not a list
            # key = value
            return self.keys.get(key)
        
        logging.debug('Key is a list: %s', key)

        # It is a list
        values = self.keys.get(key, [])

        parsed_values = []

        for value in values:
            parsed_values.append(self.parse_value(value))

        # Parse the value
        return parsed_values
        
        