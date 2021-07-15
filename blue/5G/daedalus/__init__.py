from pbr.version import VersionInfo
import pkg_resources

pkg_resources.declare_namespace(__name__)

# TODO: 3.8+ and later, use importlib: https://pypi.org/project/importlib-metadata/
__version__ = VersionInfo('networkml').semantic_version().release_string()
