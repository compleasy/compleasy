from django import template
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince

register = template.Library()

@register.filter(name='boolean_status')
def boolean_status(value):
    """ Return 'enabled' if value is True, 'disabled' otherwise """
    return 'enabled' if value else 'disabled'

@register.filter(name='boolean_icon')
def boolean_icon(value):
    """ Return a checkmark icon if value is True, a cross icon otherwise """
    checkmark = '''<span class="text-green-700"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6 ">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg><span>'''
    cross = '''<span class="text-red-700"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg></span>'''
    if value:
        return mark_safe(checkmark)
    return mark_safe(cross)


@register.filter(name='format_csv_line')
def format_csv_line(value, separator=', '):
    """ Convert a list to a string """
    if not value:
        return ''
    
    if not isinstance(value, list):
        return value
    
    return separator.join(value)

@register.filter(name='split_messages')
def split_messages(value, arg):
    """ Split a string into a list of messages using the given separator """
    try:
        parts = value.split(arg)
        # Remove empty parts (part is empty or contains just a -)
        parts = [part for part in parts if part and part != '-']
        # Strip "text:" from the beginning of each part
        parts = [part.split('text:', 1)[1] if 'text:' in part else part for part in parts]
        return parts
    except (ValueError, AttributeError):
        return [value, '']

@register.filter(name='shorten_string')
def shorten_string(value, arg):
    """ Shorten a string to the given length """
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

@register.filter(name='distro_icon')
def distro_icon(value):
    """
    Return an SVG icon based on the distribution name
    Icons are from Techicons (https://techicons.dev/icons/debian)
    """

    ubuntu = '<svg class="w-6 ml-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><path fill="#DD4814" d="M64 3.246C30.445 3.246 3.245 30.446 3.245 64c0 33.552 27.2 60.754 60.755 60.754 33.554 0 60.755-27.202 60.755-60.754 0-33.554-27.2-60.754-60.755-60.754zm13.631 20.922a8.108 8.108 0 1114.046 8.108A8.105 8.105 0 0180.6 35.243a8.11 8.11 0 01-2.969-11.075zM64 28.763c3.262 0 6.417.453 9.414 1.281a11.357 11.357 0 005.548 8.042 11.378 11.378 0 009.725.789c5.998 5.898 9.901 13.919 10.47 22.854l-11.558.17C86.532 49.796 76.377 40.306 64 40.306a23.6 23.6 0 00-9.98 2.203L48.383 32.41A35.116 35.116 0 0164 28.763zM22.689 72.112A8.112 8.112 0 0114.576 64a8.111 8.111 0 018.113-8.113 8.113 8.113 0 010 16.225zm7.191.722A11.377 11.377 0 0034.08 64c0-3.565-1.639-6.747-4.2-8.836 2.194-8.489 7.475-15.738 14.571-20.483l5.931 9.934C44.29 48.902 40.308 55.984 40.308 64s3.981 15.098 10.074 19.383l-5.931 9.937c-7.099-4.744-12.38-11.995-14.571-20.486zm58.831 33.964a8.105 8.105 0 01-11.077-2.969c-2.241-3.877-.911-8.835 2.969-11.076 3.877-2.239 8.838-.908 11.077 2.969a8.106 8.106 0 01-2.969 11.076zm-.024-17.673a11.357 11.357 0 00-9.725.788 11.36 11.36 0 00-5.547 8.042A35.232 35.232 0 0164 99.239a35.097 35.097 0 01-15.616-3.649l5.636-10.1A23.6 23.6 0 0064 87.694c12.378 0 22.532-9.488 23.596-21.592l11.561.169c-.569 8.935-4.472 16.956-10.47 22.854z"/></svg>'
    debian = '<svg class="w-6 ml-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><path fill="#A80030" d="M73.776 67.531c-2.065.028.391 1.063 3.087 1.479a27.453 27.453 0 002.023-1.741c-1.679.41-3.387.419-5.11.262m11.086-2.763c1.229-1.697 2.127-3.556 2.442-5.478-.276 1.369-1.019 2.553-1.72 3.801-3.86 2.431-.363-1.443-.002-2.916-4.15 5.225-.57 3.133-.72 4.593m4.093-10.648c.249-3.72-.733-2.544-1.063-1.125.384.201.69 2.622 1.063 1.125M65.944 3.283c1.102.198 2.381.35 2.202.612 1.206-.263 1.48-.506-2.202-.612m2.202.613l-.779.161.725-.064.054-.097m34.372 51.634c.123 3.34-.978 4.961-1.969 7.829l-1.786.892c-1.46 2.838.142 1.802-.903 4.059-2.281 2.027-6.921 6.345-8.406 6.738-1.084-.023.734-1.278.972-1.771-3.052 2.098-2.449 3.147-7.118 4.422l-.136-.305c-11.516 5.417-27.51-5.318-27.299-19.966-.123.931-.349.697-.605 1.074-.594-7.537 3.481-15.107 10.353-18.196 6.722-3.329 14.602-1.963 19.417 2.524-2.644-3.465-7.909-7.137-14.148-6.793-6.111.097-11.828 3.98-13.735 8.196-3.132 1.972-3.495 7.6-4.859 8.628-1.835 13.491 3.453 19.318 12.398 26.175 1.407.949.396 1.093.587 1.815-2.972-1.392-5.694-3.493-7.931-6.065 1.186 1.739 2.468 3.429 4.125 4.756-2.803-.949-6.546-6.79-7.64-7.028 4.832 8.649 19.599 15.169 27.333 11.935-3.579.131-8.124.073-12.145-1.413-1.688-.869-3.984-2.669-3.574-3.007 10.553 3.944 21.456 2.988 30.586-4.333 2.323-1.81 4.861-4.887 5.594-4.93-1.105 1.661.188.8-.66 2.266 2.316-3.733-1.005-1.521 2.394-6.448l1.256 1.729c-.467-3.098 3.848-6.861 3.41-11.762.99-1.499 1.104 1.612.054 5.061 1.457-3.825.384-4.44.759-7.597.404 1.062.935 2.188 1.208 3.308-.95-3.696.975-6.226 1.45-8.373-.467-.208-1.464 1.634-1.692-2.732.034-1.896.528-.993.718-1.46-.373-.215-1.349-1.668-1.944-4.456.431-.655 1.151 1.698 1.739 1.795-.378-2.217-1.028-3.907-1.053-5.609-1.713-3.579-.606.478-1.996-1.536-1.823-5.687 1.513-1.32 1.738-3.903 2.763 4.003 4.339 10.208 5.062 12.777-.552-3.133-1.443-6.168-2.532-9.105.839.354-1.352-6.446 1.091-1.943-2.609-9.6-11.166-18.569-19.038-22.778.962.881 2.179 1.989 1.743 2.162-3.915-2.331-3.227-2.513-3.787-3.498-3.19-1.297-3.399.104-5.511.003-6.012-3.188-7.171-2.85-12.703-4.848l.252 1.177c-3.984-1.327-4.641.503-8.945.004-.263-.205 1.379-.74 2.73-.937-3.85.508-3.67-.759-7.438.14.929-.651 1.909-1.082 2.9-1.637-3.139.191-7.495 1.828-6.151.339-5.121 2.286-14.218 5.493-19.322 10.28l-.161-1.073c-2.339 2.809-10.2 8.387-10.826 12.022l-.625.146c-1.218 2.06-2.004 4.396-2.97 6.517-1.592 2.713-2.334 1.044-2.107 1.469-3.132 6.349-4.687 11.683-6.03 16.057.958 1.432.022 8.614.385 14.364-1.572 28.394 19.928 55.962 43.43 62.329 3.445 1.23 8.567 1.184 12.924 1.311-5.141-1.471-5.806-.778-10.813-2.525-3.614-1.701-4.405-3.644-6.964-5.864l1.014 1.79c-5.019-1.775-2.918-2.198-7.002-3.491l1.083-1.412c-1.627-.123-4.309-2.74-5.042-4.191l-1.779.07c-2.138-2.638-3.277-4.538-3.194-6.011l-.575 1.024c-.652-1.119-7.865-9.893-4.123-7.85-.696-.637-1.62-1.035-2.622-2.856l.762-.871c-1.802-2.316-3.315-5.287-3.2-6.276.96 1.298 1.627 1.54 2.287 1.763-4.548-11.285-4.803-.622-8.248-11.487l.729-.059c-.559-.842-.898-1.756-1.347-2.652l.316-3.161c-3.274-3.786-.916-16.098-.443-22.851.328-2.746 2.733-5.669 4.563-10.252l-1.114-.192c2.131-3.717 12.167-14.928 16.815-14.351 2.251-2.829-.446-.011-.886-.723 4.945-5.119 6.5-3.617 9.838-4.537 3.6-2.137-3.089.833-1.383-.815 6.223-1.589 4.41-3.613 12.528-4.42.857.487-1.987.752-2.701 1.385 5.185-2.536 16.408-1.959 23.697 1.408 8.458 3.952 17.961 15.638 18.336 26.631l.427.114c-.216 4.37.669 9.424-.865 14.066l1.043-2.201M51.233 70.366l-.29 1.448c1.357 1.845 2.435 3.843 4.167 5.283-1.246-2.434-2.173-3.44-3.877-6.731m3.208-.126c-.718-.795-1.144-1.751-1.62-2.704.456 1.675 1.388 3.114 2.255 4.578l-.635-1.874m56.785-12.343l-.304.762a36.72 36.72 0 01-3.599 11.487 36.107 36.107 0 003.903-12.249M66.353 2.293c1.396-.513 3.433-.281 4.914-.617-1.93.162-3.852.259-5.75.503l.836.114M17.326 28.362c.322 2.979-2.242 4.135.567 2.171 1.506-3.39-.588-.935-.567-2.171M14.025 42.15c.646-1.986.764-3.18 1.011-4.328-1.788 2.285-.823 2.773-1.011 4.328"/></svg>'

    if 'ubuntu' in value.lower():
        return mark_safe(ubuntu)
    
    if 'debian' in value.lower():
        return mark_safe(debian)
    
@register.filter(name='substract')
def substract(value, arg):
    """ Substract arg from value """
    # Try to convert the value and arg to integers
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter(name='timesince_simple')
def timesince_simple(value):
    """
    Return only the largest time unit from timesince (e.g., "13 hours" instead of "13 hours, 18 minutes")
    """
    if not value:
        return ''
    
    try:
        time_str = timesince(value)
        # Split by comma and take only the first part
        # This gives us just the largest unit (e.g., "13 hours" from "13 hours, 18 minutes")
        return time_str.split(',')[0].strip()
    except (ValueError, TypeError, AttributeError):
        return ''