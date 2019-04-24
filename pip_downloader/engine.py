import os

from pip_downloader.compat.pip import (
    RequirementSet, RequirementTracker, TempDirectory, install_req_from_line, PyPI, PackageFinder,
    src_prefix, RequirementPreparer, Resolver, PipSession, canonicalize_name, Search, _download_http_url)


def _get_finder(session):
    return PackageFinder(
        find_links=[],
        index_urls=[PyPI.simple_url],
        session=session,
    )


def _get_session():
    return PipSession()


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
            return downloaded_packages


def create_candidates(requirements):
    """
    Take a list of :class:`InstallRequirement` and convert them to InstallationCandidates
    """
    install_candidates = []
    with _get_session() as session:
        finder = _get_finder(session=session)
        for req in requirements:
            canonical_name = canonicalize_name(req.name)
            formats = ['source', 'binary']  # All formats
            search = Search(req.name, canonical_name, formats)
            install_candidates.append(finder._link_package_versions(req.link, search))
    return install_candidates


def resolve_candidates(package_candidates):
    """
    Take the package-candidates and get all similar candidates with the same (name, version)
    """
    all_candidates = []
    with _get_session() as session:
        finder = _get_finder(session=session)
        for pcandidate in package_candidates:
            candidates = finder.find_all_candidates(pcandidate.project)
            for candidate in candidates:
                if (candidate.project == pcandidate.project and
                        candidate.version == pcandidate.version):
                    all_candidates.append(candidate)
    return all_candidates


def download_link(link, dest_dir):
    with _get_session() as session:
        _download_http_url(
            link,
            session,
            dest_dir,
            hashes=None,
            progress_bar='on',
        )
