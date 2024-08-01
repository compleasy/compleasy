import logging
import difflib

class LynisReport:
    """ Class to represent a Lynis report """

    class Diff:
        '''
        Class to represent a diff between two Lynis reports
        '''
        def __init__(self, diff):
            self.diff = diff
            self.changes = self.parse()

        def parse(self):
            '''
            Parse the diff and return the changes
            :return: dict
            '''
            changes = {
                'added': [],
                'removed': []
            }
            diff_lines = self.diff.splitlines(keepends=True)
            for line in diff_lines:
                if line.startswith('+++') or line.startswith('@@') or line.startswith('---'):
                    continue
                if line.startswith('+'):
                    changes['added'].append(line[1:])
                elif line.startswith('-'):
                    changes['removed'].append(line[1:])
            return changes
        
        def compare_delimited_values(self, old_value, new_value, delimiter='|'):
            '''
            Compare two delimited values and return the added and removed items
            :param old_value: str
            :param new_value: str
            :param delimiter: str
            :return: tuple
            '''
            old_items = set(old_value.split(delimiter))
            new_items = set(new_value.split(delimiter))
            added_items = new_items - old_items
            removed_items = old_items - new_items
            return list(added_items), list(removed_items)
        
        def analyze(self, ignore_keys=[]):
            changes = self.changes
            change_details = {
                'added': [],
                'removed': [],
                'changed': [],
            }

            added_dict = {line.split('=')[0].strip(): line.split('=', 1)[1].strip() for line in changes['added'] if '=' in line}
            removed_dict = {line.split('=')[0].strip(): line.split('=', 1)[1].strip() for line in changes['removed'] if '=' in line}

            # Detect added and removed fields
            for key in added_dict:
                if key in ignore_keys:
                    continue
                
                if key in removed_dict:
                    old_value = removed_dict[key]
                    new_value = added_dict[key]
                    
                    if old_value != new_value:
                        if "|" in old_value or "|" in new_value:
                            added_items, removed_items = self.compare_delimited_values(old_value, new_value)
                            change_details['changed'].append((key, 'added_items', added_items))
                            change_details['changed'].append((key, 'removed_items', removed_items))
                        else:
                            change_details['changed'].append((key, old_value, new_value))
                else:
                    change_details['added'].append({key: added_dict[key]})
            
            for key in removed_dict:
                if key in ignore_keys:
                    continue
                
                if key not in added_dict:
                    change_details['removed'].append({key: removed_dict[key]})
            
            return change_details



    def __init__(self, full_report):
        self.keys = {}
        self.report = full_report
        self.report = self.clean_full_report()
        self.keys = self.parse_report()
        self.generate_custom_variables()
    
    def diff(self, new_full_report):
        """
        Generate a diff between two Lynis reports
        :param new: LynisReport object
        :return: diff string
        """
        old_report = self.get_full_report()
        new_report = new_full_report

        diff = difflib.unified_diff(
            old_report.splitlines(keepends=True), 
            new_report.splitlines(keepends=True), 
            lineterm=''
        )
        return ''.join(diff)
    
    def apply_diff(self, diff):
        """
        Apply a diff to a Lynis report
        :param diff: diff string
        :return: patched report
        """
        logging.debug('Original report size: %d bytes', len(self.get_full_report()))
        logging.debug('Diff size: %d bytes', len(diff))

        original_lines = self.get_full_report().splitlines(keepends=True)
        diff_lines = diff.splitlines(keepends=True)

        # Combine original lines and diff lines
        full_diff = list(difflib.unified_diff(original_lines, original_lines)) + diff_lines

        # Apply the full diff to reconstruct the report
        patched_lines = list(difflib.restore(full_diff, 1))
        return ''.join(patched_lines)

    def clean_full_report(self):
        """
        Clean invalid keys from the report
        - Remove invalid tests from the report (deprecated or not relevant)
        More info: https://cisofy.com/lynis/controls/
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
        