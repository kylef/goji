#!/usr/bin/env python

from setuptools import setup

setup(
    name='goji',
    version='0.1.0',
    url='https://github.com/kylef/goji',
    author='Kyle Fuller',
    author_email='inbox@kylefuller.co.uk',
    packages=('goji',),
    install_Requires=('requests', 'manage.py'),
    entry_points={
        'console_scripts': (
            'goji = goji:main',
        )
    },
    test_suite='goji.tests',
)

