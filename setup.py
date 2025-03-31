#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs
from setuptools import setup, find_packages


setup(
    name='sphinxcontrib-images',
    version='0.9.2',
    url='https://github.com/sphinx-contrib/images',
    download_url='https://pypi.python.org/pypi/sphinxcontrib-images',
    project_urls={
        'Bug Tracker': 'https://github.com/sphinx-contrib/images/issues',
        'Documentation': 'https://sphinxcontrib-images.readthedocs.io/',
    },
    license='Apache 2',
    author=u'Tomasz Czyż',
    author_email='tomasz.czyz@gmail.com',
    description='Sphinx extension for thumbnails',
    long_description=codecs.open('README.rst', encoding="utf8").read(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Documentation',
    ],
    entry_points={
        'console_scripts':[
            'sphinxcontrib-images=sphinxcontrib.images:main',
        ],
        'sphinxcontrib.images.backend':[
            'LightBox2 = sphinxcontrib_images_lightbox2:LightBox2',
            'FakeBackend = sphinxcontrib_images_lightbox2:LightBox2',
        ]
    },
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['wheel'],
    install_requires=['sphinx>=1.8.5,<2.0;python_version<"3.0"',
                      'sphinx>=2.0;python_version>="3.0"',
                      'requests>2.2,<3'],
    namespace_packages=['sphinxcontrib'],
)
