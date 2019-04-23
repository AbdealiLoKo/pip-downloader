# pip-downloader
To enable offline installs of python packages, `pip download` exists. But is not useful
when trying to create a local folder of packages installable in different environments.

`pip-downloader` aims to solve this problem in a different approach from the `pip download`,
it downloads all packages and their dependencies provided and retain multiple distributions
(binary/source) as needed for the target installation locations

## Aim
The project aims to solve the following issues:
 - Dependencies mentioned in `setup_requires` should be available for offline usage
 - Build Dependencies should be downloaded and available in case the source distribution is used
 - Ability to specify whcih target OS the offline installation should be available
   for `windows`, `linux`, etc.
 - Ability to specify whcih target python version the offline installation should be available
   for `36`, `27`, etc.
