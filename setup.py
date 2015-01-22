# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

import pytity


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='pytity',
    version=pytity.__version__,
    url='http://github.com/marienfressinaud/pytity',
    license='MIT License',
    description='A entity system module written in Python.',
    long_description=open('README.md').read(),
    author='Marien Fressinaud',
    author_email='dev@marienfressinaud.fr',
    tests_require=['pytest'],
    install_requires=[],
    cmdclass={
        'test': PyTest
    },
    packages=['pytity'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only'
    ],
    extras_require={
        'testing': ['pytest'],
    }
)
