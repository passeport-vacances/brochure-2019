# -*- coding: utf-8 -*-
'''
Copyright 2019 Jacques Supcik

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Filename: setup.py
Created Date: 2019-03-31
Author: Jacques Supcik
'''

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()  # pylint: disable=invalid-name

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
        'jinja2',
        'PyMySQL',
        'records',
        'PyYAML',
        'Click',
        'Flask',
        'py3wetransfer'
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
