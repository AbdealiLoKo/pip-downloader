import importlib
import logging
from contextlib import contextmanager

import pip
import pkg_resources


def from_pip_import(module_path):
    """
    Import the given module from pip.

    :param module_path: The path to the module that needs to be imported.
                        Example: `models.index`
                        If a list is provided, it tries all the module-paths in the given order.
                        This is useful to try multiple paths for different versions.
    """
    prefixes = ['pip._internal', 'pip']
    if not isinstance(module_path, (tuple, list)):
        module_path = [module_path]
    search_order = ['{0}.{1}'.format(p, pth) for p in prefixes for pth in module_path]
    for to_import in search_order:
        to_import, package = to_import.rsplit('.', 1)
        try:
            imported = importlib.import_module(to_import)
        except ImportError as err:
            logging.debug('ImportError when importing "{}": {}'.format(to_import, err))
            continue
        else:
            return getattr(imported, package)
    raise ImportError('Unable to find module in pip: {}'.format(module_path))


# Pip 18 uses a requirement tracker to prevent fork bombs
if pkg_resources.parse_version(pip.__version__) > pkg_resources.parse_version('18.0'):
    RequirementTracker = from_pip_import('req.req_tracker.RequirementTracker')
else:
    @contextmanager
    def RequirementTracker():  # noqa: N802
        yield


RequirementSet = from_pip_import('req.req_set.RequirementSet')
Wheel = from_pip_import('wheel.Wheel')
TempDirectory = from_pip_import('utils.temp_dir.TempDirectory')
InstallRequirement = from_pip_import('req.req_install.InstallRequirement')
PyPI = from_pip_import('models.index.PyPI')
Link = from_pip_import('models.link.Link')
PipSession = from_pip_import('download.PipSession')
src_prefix = from_pip_import('locations.src_prefix')
RequirementPreparer = from_pip_import('operations.prepare.RequirementPreparer')
Resolver = from_pip_import('resolve.Resolver')
PackageFinder = from_pip_import('index.PackageFinder')
PipSession = from_pip_import('download.PipSession')
_egg_info_matches = from_pip_import('index._egg_info_matches')
SUPPORTED_EXTENSIONS = from_pip_import('utils.misc.SUPPORTED_EXTENSIONS')
WHEEL_EXTENSION = from_pip_import('utils.misc.WHEEL_EXTENSION')
InvalidWheelFilename = from_pip_import('exceptions.InvalidWheelFilename')
from pip._vendor.packaging.utils import canonicalize_name  # noqa: F401

# pip 18.1 has refactored InstallRequirement constructors use by pip-tools.
if pkg_resources.parse_version(pip.__version__) < pkg_resources.parse_version('18.1'):
    install_req_from_line = InstallRequirement.from_line
    install_req_from_editable = InstallRequirement.from_editable
else:
    install_req_from_line = from_pip_import('req.constructors.install_req_from_line')
    install_req_from_editable = from_pip_import('req.constructors.install_req_from_editable')
