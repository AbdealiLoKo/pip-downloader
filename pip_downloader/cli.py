import os
import sys

import click

from pip_downloader.engine import resolve_packages, fetch_all_links, download_link


@click.group()
def main():
    """
    pip-downloader downloads dependencies and packages from pip for offline
    usage.
    """


@main.command(
    name='list',
    short_help='List all packages that are needed for installation.')
@click.argument('packages', nargs=-1, required=False)
def list_command(packages, platform=None, python=None):
    """
    Fetch information about the packages that are provided.
    Can be thought of as a dry-run for the actual download.
    """
    resolved_packages = resolve_packages(packages)
    for pkg_name, pkg_version in resolved_packages:
        print('Found', pkg_name, pkg_version, '...')
        links = fetch_all_links(pkg_name, pkg_version)
        for ilink, link in enumerate(links):
            print(' -', ilink + 1, '/', len(links), '-', link.filename)


@main.command(name='download', short_help='Download required packages')
@click.option(
    '--dest', type=click.Path(file_okay=False, writable=True), required=True,
    help='The directory to dump.')
# @click.option(
#     '--platform', type=click.Choice(['linux', 'osx', 'win']), default='linux',
#     help='The platform to download for.')
# @click.option(
#     '--python', type=click.Choice(['33', '34', '35', '36', '37']),
#     help='The python version to download for.')
@click.argument('packages', nargs=-1, required=False)
def download_command(packages, dest, platform=None, python=None):
    """
    Download all available files for the packages provided.
    """
    resolved_packages = resolve_packages(packages)
    os.makedirs(dest, exist_ok=True)
    for pkg_name, pkg_version in resolved_packages:
        print('Found', pkg_name, pkg_version, '...')
        links = fetch_all_links(pkg_name, pkg_version)
        for ilink, link in enumerate(links):
            print(' -', ilink + 1, '/', len(links), '-', link.filename)
            download_link(link, dest)


if __name__ == '__main__':
    sys.exit(main())
