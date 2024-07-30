import os
import logging

class LynisReport:
    def __init__(self, full_report):
        self.keys = {}
        self.report = full_report
        self.report = self.clean_full_report()
        self.keys = self.parse_report()
        self.generate_custom_variables()

    def clean_full_report(self):
        """
        Clean invalid keys from the report
        - Remove invalid tests from the report (deprecated or not relevant)
        """
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
    
    def generate_custom_variables(self):
        """Add custom variables to the report."""

        # Generate count variables
        count_keys = self.generate_count_variables()
        for key, value in count_keys.items():
            self.set(key, value)
        
        # Generate filtered IPv4 addresses
        # The one(s) connected to the default gateway(s)
        self.set('primary_ipv4_addresses', self.get_filtered_ipv4_addresses())

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
        #self.keys.update(count_keys)
        return count_keys
    
    def get(self, key):
        """Get the value of a specific key."""
        return self.keys.get(key)
    
    def set(self, key, value):
        """Set the value of a specific key."""
        self.keys[key] = value
    
    def get_filtered_ipv4_addresses(self):
        """Filter IPv4 addresses connected to default gateway(s)"""
        default_gateways = self.get('default_gateway')
        ipv4_addresses = self.get('network_ipv4_address')
        filtered_addresses = []

        if not ipv4_addresses:
            return ['-']

        # If default_gateways is empty return all network_ipv4_addresses
        if not default_gateways:
            return ipv4_addresses

        for default_gateway in default_gateways:
            # We assume network prefix is /24
            # Example: default gateway 192.168.1.1
            # network prefix: 192.168.1
            gateway_network_prefix = '.'.join(default_gateway.split('.')[:3])
            for ipv4_address in ipv4_addresses:
                if gateway_network_prefix in ipv4_address:
                    filtered_addresses.append(ipv4_address)
        # Convert list to string
        logging.debug(f'Filtered IPv4 addresses: {filtered_addresses}')
        return filtered_addresses
        