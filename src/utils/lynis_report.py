import logging
import difflib
from typing import Dict, List, Tuple, Any

class LynisReport:
    """
    Class to represent a Lynis report.

    = About Lynis Reports =

    Lynis report 1.0 is formatted as key-value pairs separated by '=', each pair on a new line.

    Example:

    # Lynis Report
    report_version_major=1
    report_version_minor=0
    linux_version=Ubuntu

    == Keys ==

    The report contains the following types of keys:
    - Single key-value pairs
    - List key-value pairs (indicated by '[]' in the key)
    - Comments (lines starting with '#')

    == Values ==
    
    The value can be a simple value or a delimiter-separated value ('|' or ',').
    """

    class LynisData:
        """
        Class to represent a Lynis value string, present in list key-value pairs.

        The following types are supported:
        - Single value
        - Multiple values delimited by '|' or by ','
        - Multiple values delimited by '|' inner and ',' outer

        This class will parse the raw string and return a list of lists containing the values.
        """
        class SimpleValue:
            def __init__(self, raw_value: str):
                self.value = raw_value

            def get (self) -> str:
                return self.value

        class SimpleList:
            def __init__(self, raw_value: str, delimiter: str = '|'):
                self.raw_value = raw_value
                self.delimiter = delimiter
                self.values = self._parse_values()

            def _parse_values(self) -> List[str]:
                return self.raw_value.split(self.delimiter)
            
            def get(self) -> List[str]:
                return self.values
        
        class NestedList:
            def __init__(self, raw_value: str, outer_delimiter: str = ',', inner_delimiter: str = '|'):
                self.raw_value = raw_value
                self.outer_delimiter = outer_delimiter
                self.inner_delimiter = inner_delimiter
                self.values = self._parse_values()

            def _parse_values(self) -> List[List[str]]:
                return [line.split(self.inner_delimiter) for line in self.raw_value.split(self.outer_delimiter)]
            
            def get(self) -> List[List[str]]:
                return self.values
            
        def __init__(self, raw_value: str):
            self.raw_value = raw_value
            # Detect the type of value and assign the correct class
            if '|' in raw_value and ',' in raw_value:
                self.value = self.NestedList(raw_value, ',', '|')
            elif '|' in raw_value:
                self.value = self.SimpleList(raw_value, '|')
            elif ',' in raw_value:
                self.value = self.SimpleList(raw_value, ',')
            else:
                self.value = self.SimpleValue(raw_value)
            
        def get(self) -> Any:
            return self.value.get()


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
        
        def _compare_delimited_values(self, old_value: str, new_value: str) -> Tuple[List[str], List[str]]:
            '''
            Compare two delimited values and return the added and removed items
            :param old_value: str
            :param new_value: str
            :param delimiter: str
            :return: tuple
            '''
            old_value = LynisReport.LynisData(old_value).get()
            new_value = LynisReport.LynisData(new_value).get()

            # Compare the values between the two lists and return the added and removed items
            added_items = list(set(new_value) - set(old_value))
            removed_items = list(set(old_value) - set(new_value))
            logging.debug('Added items: %s', added_items)
            logging.debug('Removed items: %s', removed_items)
            return added_items, removed_items
        
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

            try:
                added_dict = {line.split('=')[0].strip(): line.split('=', 1)[1].strip() for line in changes['added'] if '=' in line}
                removed_dict = {line.split('=')[0].strip(): line.split('=', 1)[1].strip() for line in changes['removed'] if '=' in line}
            except (ValueError, IndexError) as e:
                logging.error('Error parsing diff: %s', e)
                return change_details

            # Detect added and removed fields
            for key in added_dict:
                if key in ignore_keys:
                    continue
                
                if key in removed_dict:
                    old_value = removed_dict[key]
                    new_value = added_dict[key]
                    
                    if old_value != new_value:
                        logging.debug('Changed key: %s', key)
                        if "|" in old_value or "|" in new_value or "," in old_value or "," in new_value:
                            logging.debug('Delimited value detected. Looking for added and removed items.')
                            # If the value is a delimited value, compare the values and get the added and removed items
                            added_items, removed_items = self._compare_delimited_values(old_value, new_value)
                            
                            # Add added items to the added list
                            if added_items:
                                for item in added_items:
                                    # if key-value is already in the added list, do not add
                                    if {key: added_items} in change_details['added']:
                                        break
                                    change_details['added'].append({key: added_items})
                            
                            # Add removed items to the removed list
                            if removed_items:
                                for item in removed_items:
                                    # if key-value is already in the removed list, do not add
                                    if {key: removed_items} in change_details['removed']:
                                        break
                                    change_details['removed'].append({key: removed_items})

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
        self.keys = {}

        try:
            self.report = self._clean_full_report()
            self.keys = self._parse_report()
            self._generate_custom_variables()
        except Exception as e:
            logging.error(f'Error initializing LynisReport: {e}')
    
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
            # Parse the value using the LynisData class
            value = self.LynisData(value).get()
            
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
        