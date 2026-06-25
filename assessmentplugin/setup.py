"""Setup for assessmentplugin XBlock."""

import os

from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.
    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='assessmentplugin-xblock',
    version='0.1.0',
    description='Assessment XBlock — interactive Coppin assessments rendered with shared React UI',
    license='AGPL v3',
    packages=[
        'assessmentplugin',
    ],
    install_requires=[
        'XBlock',
        'xblock-utils',
        'requests',
    ],
    entry_points={
        'xblock.v1': [
            'assessmentplugin = assessmentplugin:AssessmentXBlock',
        ]
    },
    package_data=package_data("assessmentplugin", ["static", "public"]),
)
