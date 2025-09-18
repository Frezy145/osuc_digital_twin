"""
Setup configuration for OSUC Digital Twin Project.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
def read_requirements(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#') and not line.startswith('-r')]
    except FileNotFoundError:
        return []

setup(
    name='osuc-digital-twin',
    version='0.1.0',
    description='OSUC Digital Twin Project - Master 2 2025/2026',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='OSUC Digital Twin Team',
    author_email='contributors@osuc-digital-twin.org',
    url='https://github.com/Frezy145/osuc_digital_twin',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=[],  # Will be populated as project develops
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'isort>=5.10.0',
            'flake8>=5.0.0',
            'pre-commit>=2.20.0',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords='digital-twin simulation modeling education research',
    project_urls={
        'Bug Reports': 'https://github.com/Frezy145/osuc_digital_twin/issues',
        'Source': 'https://github.com/Frezy145/osuc_digital_twin',
        'Documentation': 'https://github.com/Frezy145/osuc_digital_twin/wiki',
        'Discussions': 'https://github.com/Frezy145/osuc_digital_twin/discussions',
    },
)