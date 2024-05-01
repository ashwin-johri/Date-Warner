from django import template
import re

register = template.Library()

@register.filter
def basename(value):
    # Extract the filename from a URL
    match = re.search(r'/([^/]+)\?', value)
    if match:
        return match.group(1)
    return value

@register.filter
def filename(value):
    """Extracts the original filename from a URL or path, removing any URL parameters, storage system appendices, and unique identifiers."""
    # Split the URL on '/' and get the last part to ensure we are working with the filename part only
    name = value.split('/')[-1]
    # Remove any URL parameters
    name = re.split('\?|&', name)[0]
    # Strip out the unique suffix Django adds (pattern typically looks like '_xyz')
    name = re.sub(r'_[\w]+(\.\w+)$', r'\1', name)
    return name
# def filename(value):
#     """Extracts the original filename from a URL, removing any URL parameters and storage system appendices."""
#     # Split the URL on '/' and get the last part to ensure we are working with the filename part only
#     name = value.split('/')[-1]
#     # Remove any URL parameters
#     name = re.split('\?|&', name)[0]
#     # Attempt to remove the automatically appended unique identifier by Django's storage
#     name = re.sub(r'_[\w]+(\.\w+)$', r'\1', name)
#     return name