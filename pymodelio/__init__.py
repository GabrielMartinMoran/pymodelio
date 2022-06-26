# flake8: noqa

__version__ = '0.0.5'

# constants
from .constants import UNDEFINED

# pymodelio_model decorator
from .model import pymodelio_model

# Attribute with all aliases
from .attribute import Attribute
from .attribute import Attr
from .attribute import ModelAttribute
from .attribute import ModelAttr

# BaseModel for those who don't like the decorators :'(
from .base_model import BaseModel
