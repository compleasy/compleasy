"""
Settings module for TrikuSec.
Loads appropriate settings based on DJANGO_ENV environment variable.
"""
import os

# Determine which settings to use
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *  # noqa
elif env == 'testing':
    from .testing import *  # noqa
else:
    from .development import *  # noqa

