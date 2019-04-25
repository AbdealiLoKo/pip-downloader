import logging
import os

import requests

from pip_downloader.compat.pip import (
    RequirementSet, RequirementTracker, TempDirectory, install_req_from_line, PyPI, PackageFinder,
    src_prefix, RequirementPreparer, Resolver, PipSession, canonicalize_name, Link,
    SUPPORTED_EXTENSIONS, WHEEL_EXTENSION, Wheel, InvalidWheelFilename, _egg_info_matches)


def _get_finder(session):
    finder = PackageFinder(
        find_links=[],
        index_urls=[PyPI.simple_url],
        session=session,
    )
    return finder


def _get_session():
    return PipSession()


def _get_version_from_link(link, name):
    # Logic referenced from pip._internal.index.PackageFinder._link_package_versions()
    canonical_name = canonicalize_name(name)

    def _log_skipped_link(link, reason):
        logging.debug('Skipping link %s; %s', link, reason)

    version = None
    if link.egg_fragment:  # If egg-info is present in the link, use that
        egg_info = link.egg_fragment
        ext = link.ext
    else:  # Else: ensure it is a valid file
        egg_info, ext = link.splitext()
        if not ext:
            _log_skipped_link(link, 'not a file')
            return None
        if ext not in SUPPORTED_EXTENSIONS:
            _log_skipped_link(link, 'unsupported archive format: %s' % ext,)
            return None
        if "macosx10" in link.path and ext == '.zip':
            _log_skipped_link(link, 'macosx10 one')
            return None
        if ext == WHEEL_EXTENSION:  # If the file is a wheel, get version from that
            try:
                wheel = Wheel(link.filename)
            except InvalidWheelFilename:
                _log_skipped_link(link, 'invalid wheel filename')
                return None
            if canonicalize_name(wheel.name) != canonical_name:
                _log_skipped_link(link, 'wrong project name (not %s)' % name)
                return None
            version = wheel.version

    if not version:  # If not wheel, get from egg-info
        version = _egg_info_matches(egg_info, canonical_name)
    if not version:
        _log_skipped_link(link, 'Missing project version for %s' % name)
        return None
    logging.debug('Found link %s, version: %s', link, version)
    return version


def resolve_packages(packages):
    """
    Take a list of requirement lines and convert them to :class:`InstallRequirement` using pip.
    """
    with _get_session() as session:
        finder = _get_finder(session=session)
        with RequirementTracker() as req_tracker, TempDirectory(kind="downloader") as directory:
            requirement_set = RequirementSet()
            for pkg in packages:
                install_req = install_req_from_line(pkg)
                install_req.is_direct = True
                requirement_set.add_requirement(install_req)

            preparer = RequirementPreparer(
                build_dir=directory.path,
                src_dir=src_prefix,
                download_dir=None,
                wheel_download_dir=None,
                progress_bar='on',
                build_isolation=True,
                req_tracker=req_tracker,
            )
            resolver = Resolver(
                preparer=preparer,
                finder=finder,
                session=session,
                wheel_cache=None,
                use_user_site=False,
                upgrade_strategy='to-satisfy-only',
                force_reinstall=False,
                ignore_dependencies=False,
                ignore_requires_python=False,
                ignore_installed=True,
                isolated=False,
            )
            resolver.resolve(requirement_set)

            downloaded_packages = requirement_set.successfully_downloaded

            resolved_packages = []
            for pkg in downloaded_packages:
                pkg_version = _get_version_from_link(pkg.link, pkg.name)
                if pkg_version is not None:
                    resolved_packages.append((pkg.name, pkg_version))
            return resolved_packages


def fetch_all_links(pkg_name, pkg_version):
    """
    Take a package name, version and get all links it matches to.

    Sources: find-links, index-urls
    """
    # Logic references from: pip._internal.PackageFinder.find_all_candidates()
    available_links = []
    with _get_session() as session:
        finder = _get_finder(session=session)
        index_locations = finder._get_index_urls_locations(pkg_name)
        index_file_loc, index_url_loc = finder._sort_locations(index_locations)
        if len(index_file_loc) > 0:
            raise AssertionError(
                'Indexes with file:// not supported. Got: {}'.format(index_file_loc))
        if finder.find_links:
            raise AssertionError(
                'find-links not supported. Got: {}'.format(finder.find_links))

        url_locations = [Link(url) for url in index_url_loc]

        logging.debug('%d location(s) to search for versions of %s:',
                      len(url_locations), pkg_name)
        for location in url_locations:
            logging.debug('* %s', location)

        available_links = []
        for page in finder._get_pages(url_locations, pkg_name):
            logging.debug('Analyzing links from page %s', page.url)
            for link in page.iter_links():
                if pkg_version is None:
                    available_links.append(link)
                else:
                    link_version = _get_version_from_link(link, pkg_name)
                    if link_version == pkg_version:
                        available_links.append(link)
    return available_links


def download_link(link, dest_dir):
    resp = requests.get(link.url)
    with open(os.path.join(dest_dir, link.filename), 'wb') as fhandler:
        fhandler.write(resp.content)
