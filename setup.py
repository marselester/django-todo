#!/usr/bin/env python
from distutils.core import setup

setup(
    name='django-todo',
    version='0.1dev',
    long_description=open('README.rst').read(),
    author='marselester',
    author_email='marselester@ya.ru',
    packages=['todo', ],
    include_package_data=True,
)
