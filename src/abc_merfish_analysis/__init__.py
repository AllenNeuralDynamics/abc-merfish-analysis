"""ABC MERFISH analysis package"""
__version__ = "0.4.6"
from .abc_load_thalamus import DEFAULT_ATLAS_WRAPPER

# alias thalamus defaults for easier access
# TODO: change most import usages from global to explicit arguments (with default)
abc_load = DEFAULT_ATLAS_WRAPPER
