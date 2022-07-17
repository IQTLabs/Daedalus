import pkg_resources
from importlib.metadata import version

pkg_resources.declare_namespace(__name__)

__version__ = version('daedalus-5g')
