# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='CBG',
    version='0.3.0',
    description='Card-based game creation library',
    requires=['yaml', 'numpy', 'lxml'],
    author='Viktor Eikman',
    author_email='viktor.eikman@gmail.com',
    url='viktor.eikman.se',
    packages=['cbg'],
    package_data={'': ['*.yaml']}
    )
