import os
import sys

import click

from pip_downloader.engine import (
    resolve_packages, create_candidates, resolve_candidates, download_link)


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
    norm_packages = resolve_packages(packages)
    candidates = create_candidates(norm_packages)
    for candidate in candidates:
        print(candidate.project, candidate.version)


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
    norm_packages = resolve_packages(packages)
    candidates = create_candidates(norm_packages)
    norm_candidates = resolve_candidates(candidates)
    os.makedirs(dest, exist_ok=True)
    for candidate in norm_candidates:
        print('Downloading', candidate.project, candidate.version, candidate.location.filename, '...')
        download_link(candidate.location, dest)


if __name__ == '__main__':
    sys.exit(main())
