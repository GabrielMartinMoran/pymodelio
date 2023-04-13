# flake8: noqa

__version__ = '1.0.0'

# constants
from .constants import UNDEFINED

# Settings
from .settings.pymodelio_setting import PymodelioSetting
from .settings.pymodelio_settings import PymodelioSettings

# BaseModel for those who don't like the decorators :'(
from .base_model import BaseModel

# pymodelio_model decorator
from .decorators.model import model

pymodelio_model = model

# Attribute with all aliases
from .attribute import Attribute
from .attribute import Attr
from .attribute import ModelAttribute
from .attribute import ModelAttr

from .decorators.do_not_serialize import do_not_serialize
