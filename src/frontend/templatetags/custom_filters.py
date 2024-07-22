from django import template

register = template.Library()

@register.filter(name='boolean_status')
def boolean_status(value):
    return 'enabled' if value else 'disabled'

@register.filter(name='split_messages')
def split_messages(value, arg):
    try:
        return value.split(arg)
    except (ValueError, AttributeError):
        return [value, '']

@register.filter(name='filter_ipv4_address')
def filter_ipv4_address(value, arg):
    filtered_addresses = []
    network_ipv4_addresses = value
    default_gateways = arg

    # If default_gateways is empty return all network_ipv4_addresses
    if not default_gateways:
        return network_ipv4_addresses

    for default_gateway in default_gateways:
        # We assume network prefix is /24
        # Example: default gateway 192.168.180.1
        # network prefix: 192.168.180
        gateway_network_prefix = '.'.join(default_gateway.split('.')[:3])
        for network_ipv4_address in network_ipv4_addresses:
            if gateway_network_prefix in network_ipv4_address:
                filtered_addresses.append(network_ipv4_address)
    # Convert list to string
    filtered_addresses = ' '.join(filtered_addresses)
    return filtered_addresses

@register.filter(name='shorten_string')
def shorten_string(value, arg):
    # Return the last arg characters of the value
    return "..." + value[-arg:]