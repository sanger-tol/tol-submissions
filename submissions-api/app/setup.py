# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

# coding: utf-8

from setuptools import find_packages, setup

NAME = 'app'
VERSION = '1.1.0'
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools


setup(
    name=NAME,
    version=VERSION,
    description='Tree of Life public name API',
    author_email='',
    url='',
    keywords=['Swagger', 'Tree of Life public name API'],
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['app=main.run:main']},
    long_description="""\
    API for ToLID registry
    """
)
