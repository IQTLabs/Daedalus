import pkg_resources
from pbr.version import VersionInfo

pkg_resources.declare_namespace(__name__)

# TODO: 3.8+ and later, use importlib: https://pypi.org/project/importlib-metadata/
__version__ = VersionInfo('daedalus-5g').semantic_version().release_string()
