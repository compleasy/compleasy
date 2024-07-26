from django import template

register = template.Library()

@register.filter(name='boolean_status')
def boolean_status(value):
    return 'enabled' if value else 'disabled'

@register.filter(name='split_messages')
def split_messages(value, arg):
    try:
        parts = value.split(arg)
        # Remove empty parts (part is empty or contains just a -)
        parts = [part for part in parts if part and part != '-']
        # Strip "text:" from the beginning of each part
        parts = [part.split('text:', 1)[1] if 'text:' in part else part for part in parts]
        return parts
    except (ValueError, AttributeError):
        return [value, '']

@register.filter(name='filter_ipv4_address')
def filter_ipv4_address(value, arg):
    filtered_addresses = []
    network_ipv4_addresses = value
    default_gateways = arg

    # If default_gateways is empty return all network_ipv4_addresses
    if not default_gateways:
        return ' / '.join(network_ipv4_addresses)

    for default_gateway in default_gateways:
        # We assume network prefix is /24
        # Example: default gateway 192.168.180.1
        # network prefix: 192.168.180
        gateway_network_prefix = '.'.join(default_gateway.split('.')[:3])
        for network_ipv4_address in network_ipv4_addresses:
            if gateway_network_prefix in network_ipv4_address:
                filtered_addresses.append(network_ipv4_address)
    # Convert list to string
    filtered_addresses = ' / '.join(filtered_addresses)
    return filtered_addresses

@register.filter(name='shorten_string')
def shorten_string(value, arg):
    # Return the last arg characters of the value
    return "..." + value[-arg:]

@register.filter(name='is_version_older')
def is_version_older(version, compare_to):
    """
    Compare two versions and return True if the first version is older than the second

    Using the direct string comparison in Django templates can work for certain version numbers,
    but it may not be reliable for all cases due to how strings are compared lexicographically.
    For example, "10.0.0" would be considered less than "2.0.0" because "1" is less than "2".

    This filter converts the version strings to tuples of integers and compares them element-wise.
    """
    if not version or not compare_to:
        return False
    
    return tuple(map(int, version.split('.'))) < tuple(map(int, compare_to.split('.')))