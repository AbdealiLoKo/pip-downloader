# pip-downloader
pip-downloader helps in allowing offline installations of python packages.

`pip download` already exists, which does something similar:
 - Pro: Handles dependency resolution in the same way `pip install` does - so no confusion
 - Pro: It is useful to download all the source packages with the `--no-binary :all:` argument.
 - Con: It downloads only 1 file per package (i.e. only source or only one of the wheel files)
 - Con: For downloads of a different system (not the system you're running it from) it expects
        the package and all it's dependencies to have similar wheels (eg: If cp36m-manylinux is
        the wheel for one library, all it's dependencies should also have that wheel)

`pip-downloader` aims to solve the same issue but in a slightly different way:
 - It uses the same dependency resolution `pip download` uses but after resolving the dependencies
 - It downloads all the files (source and all wheels) available for that version of the package
This gives an experience that is more consistent with the online installation with pip as it has
all the files (all wheels and sources) for installation.

## Installation
It is recommended to use the latest version of pip (19.x) when using pip-downloader.

    pip install pip-downloader

## Usage
The command line utility `pip-downloader` should be available.

    # To get help about pip-downloader
    pip-downloader --help

    # To fetch the list of packages and their versions that downloader will download (dry-run)
    pip-downloader list pandas 

    # To download the list of packages and their versions to the provided destination
    pip-downloader download pandas --dest /tmp/pypi


To enable offline installs of python packages, `pip download` exists. But is not useful
when trying to create a local folder of packages installable in different environments.

`pip-downloader` aims to solve this problem in a different approach from the `pip download`,
it downloads all packages and their dependencies provided and retain multiple distributions
(binary/source) as needed for the target installation locations

# Known Limitations
 - Dependencies mentioned in `setup_requires` are not downloaded as pip's dependency resolution
   mechanism does not consider them at the moment. Common setup-time requirements are:
   setuptools_scm, vcversioner, numpy, etc.
 - Build dependencies mentioned in `pyproject.toml` are not downlaoded as pip's dependency manages
   install/run-time dependencies at the moment. (These are needed only if source installation is
   chosen when installing a package.)
 - When solving for packages with `sys_platform` environment markers, the package resolution will
   happen based on the machine you're running `pip-downloader` from. Need to investigate on how to
   resolve this issue.
