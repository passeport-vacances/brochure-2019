# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='brochure',
    description='Brochure for Passeport vacances Fribourg',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jacques Supcik',
    author_email='jacques@pvfr.ch',
    url='https://github.com/passeport-vacances/brochure2019',
    py_modules=['app', 'cli'],
    packages=['brochure', 'groople', 'j2latex'],
    include_package_data=True,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'Click',
        'jinja2',
    ],
    entry_points='''
        [console_scripts]
        pvfr-brochure=cli:main
    ''',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)