#!/usr/bin/env python

from setuptools import setup

setup(
    name='paikkala',
    version='0.0',
    description='Paikkavarauskala',
    author='Aarni Koskela',
    author_email='akx@desucon.fi',
    url='https://github.com/kcsry/paikkala',
    packages=['paikkala', 'paikkala.migrations'],
    package_data={'paikkala': ['static/paikkala/*']},
    include_package_data=True,
    zip_safe=False,
    install_requires=['Django>=1.8'],
    extras_require={
        'dev': [
            'pytest-django',
            'pytest-cov',
        ],
    },
)
