import logging
import difflib
from typing import Dict, List, Tuple, Any

class LynisReport:
    """
    Class to represent a Lynis report.

    = About Lynis Reports =

    Lynis report 1.0 is formatted as key-value pairs separated by '=' and lines separated by '\n'.

    Example:

    # Lynis Report
    report_version_major=1
    report_version_minor=0
    linux_version=Ubuntu

    == Types of keys ==

    The report contains the following types of keys:
    - Single key-value pairs
    - List key-value pairs (indicated by '[]' in the key)
    - Comments (lines starting with '#')

    == Types of values ==
    
    The values can be strings or lists of strings:
    Example:
    
    # List key-value pair with multiple values delimited by '|'
    suggestion[]=LYNIS|This release is more than 4 months old. Check the website or GitHub to see if there is an update available.|-|-|

    # Single key-value pair with a string value
    binary_paths=/snap/bin,/usr/bin,/usr/sbin,/usr/local/bin,/usr/local/sbin

    # List key-value pair with multiple values delimited by '|', itself delimited by ','
    network_listen[]=raw,ss,v1|udp|224.0.0.251:5353|chrome|
    """

    class Diff:
        '''
        Class to represent a diff between two Lynis reports
        '''
        def __init__(self, diff):
            self.diff = diff
            self.changes = self._parse_diff()

        def _parse_diff(self) -> Dict[str, List[str]]:
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
        
        def _compare_delimited_values(self, old_value: str, new_value: str, delimiter: str = '|') -> Tuple[List[str], List[str]]:
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
        
        def analyze(self, ignore_keys: List[str] = []) -> Dict[str, Any]:
            '''
            Analyze the parsed changes
            :param ignore_keys: List of keys to ignore
            :return: dict with changes categorized
            '''
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
                            added_items, removed_items = self._compare_delimited_values(old_value, new_value)
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



    def __init__(self, full_report: str):
        self.report = full_report
        self.report = self._clean_full_report()
        self.keys = self._parse_report()
        self._generate_custom_variables()
    
    def diff(self, new_full_report: str) -> str:
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
    
    def apply_diff(self, diff: str) -> str:
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

    def _clean_full_report(self) -> str:
        """
        Clean invalid keys from the report
        - Remove invalid tests from the report (deprecated or not relevant)
        More info: https://cisofy.com/lynis/controls/
        """
        invalid_tests = ['DEB-0280', 'DEB-0285', 'DEB-0520', 'DEB-0870', 'DEB-0880']

        # Remove lines with invalid tests
        report_lines = self.report.split('\n')
        cleaned_lines = [line for line in report_lines if not any(test in line for test in invalid_tests)]
        return '\n'.join(cleaned_lines)

    def get_full_report(self) -> str:
        """Return the full report content."""
        return self.report

    def _parse_report(self) -> Dict[str, Any]:
        """Parse the report"""
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
    
    def _generate_custom_variables(self) -> None:
        """Add custom variables to the report."""

        # Generate count variables
        count_keys = self._generate_count_variables()
        for key, value in count_keys.items():
            self.set(key, value)
        
        # Generate filtered IPv4 addresses
        # The one(s) connected to the default gateway(s)
        self.set('primary_ipv4_addresses', self._get_filtered_ipv4_addresses())

    def get_parsed_report(self) -> Dict[str, Any]:
        """Return the parsed report."""
        return self.keys

    def _generate_count_variables(self) -> Dict[str, int]:
        """Generate count variables for lists."""
        
        count_keys = {}
        for key, value in self.keys.items():
            if isinstance(value, list):
                count_keys[f'{key}_count'] = len(value)
                #logging.debug(f'Generated count key: {key}_count with value: {len(value)}')
        #self.keys.update(count_keys)
        return count_keys
    
    def get(self, key: str) -> Any:
        """Get the value of a specific key."""
        return self.keys.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set the value of a specific key."""
        self.keys[key] = value
    
    def _get_filtered_ipv4_addresses(self) -> List[str]:
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
        