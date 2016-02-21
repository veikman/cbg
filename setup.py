# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='CBG',
    version='0.9.1~alpha1',
    description='Card-based game creation library',
    requires=['yaml', 'numpy', 'lxml'],
    author='Viktor Eikman',
    author_email='viktor.eikman@gmail.com',
    url='viktor.eikman.se',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    packages=['cbg', 'cbg.content', 'cbg.sample', 'cbg.svg'],
    )
