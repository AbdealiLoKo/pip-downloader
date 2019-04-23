# pip-downloader
To enable offline installs of python packages, `pip download` exists. But is not useful
when trying to create a local folder of packages installable in different environments.

`pip-downloader` aims to solve this problem in a different approach from the `pip download`,
it downloads all packages and their dependencies provided and retain multiple distributions
(binary/source) as needed for the target installation locations
