#!/usr/bin/env python
from distutils.core import setup

setup(
    name='django-todo',
    version='0.1dev',
    long_description=open('README.rst').read(),
    author='marselester',
    author_email='marselester@ya.ru',
    packages=[
        'todo',
        'todo.templatetags',
    ],
    include_package_data=True,
    install_requires=[
        'django-model-utils',
        'pytils',
    ]
)
