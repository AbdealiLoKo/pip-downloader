#!/usr/bin/env python

from setuptools import find_packages, setup

version_ns = {}
with open('pip_downloader/__init__.py') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version_ns)
            break

setup(
    name='pip-downloader',
    version=version_ns['__version__'],
    py_modules=find_packages(include=['pip_downloader', 'pip_downloader.*']),
    description='Download packages from pip for offline usage.',
    long_description=open('README.rst').read(),
    license='MIT',
    author='AbdealiJK',
    author_email='abdealikothari@gmail.com',
    url='https://github.com/AbdealiJK/pip-downloader',
    install_requires=['click', 'requests'],
    entry_points={
        'console_scripts': ['pip-downloader = pip_downloader.cli:main'],
    },
)
