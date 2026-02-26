# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import os
from setuptools import setup, find_packages


def add_init_files():
    """
    Ensures that the '__init__.py' file exists within the specified target directory.
    This function is used to programmatically create an '__init__.py' if it's not present,
    ensuring the directory is treated as a Python package.

    The function checks if the 'target_dir' exists and then ensures that '__init__.py'
    is present. If the directory does not exist, it outputs an error message.
    """
    target_dir = './src/lookerctl'

    # Check if the target directory exists
    if os.path.exists(target_dir):
        # Construct the path to the __init__.py file within the target directory
        init_path = os.path.join(target_dir, '__init__.py')
        # Create __init__.py if it does not exist
        if not os.path.exists(init_path):
            with open(init_path, 'w') as file:
                pass
                file.close()  # Only creating the file, no content needed
    else:
        # Output error if the target directory does not exist
        print("The directory lookerctl does not exist at the root level.")

# Create __init__.py files as necessary
add_init_files()

# Setup function call which defines package configuration
setup(
    name='lookerctl',
    version='0.1.0',  # Define the version of your package
    packages=find_packages(),  # Automatically find and list all packages
    include_package_data=True,  # Include all data files specified in MANIFEST.in
    install_requires=[
        # List all dependencies required by the package
        'attrs==24.3.0',
        'boto3==1.36.2',
        'botocore==1.36.2',
        'build==1.2.2.post1',
        'cattrs==24.1.2',
        'certifi==2024.12.14',
        'charset-normalizer==3.4.1',
        'click==8.0.3',
        'idna==3.10',
        'iniconfig==2.0.0',
        'jmespath==1.0.1',
        'looker-sdk==25.0.0',
        'numpy==2.2.2',
        'packaging==24.2',
        'pandas==2.2.3',
        'pluggy==1.5.0',
        'pyproject_hooks==1.2.0',
        'pytest==8.3.4',
        'flake8==7.1.1',
        'python-dateutil==2.9.0.post0',
        'python-dotenv==1.0.1',
        'pytz==2024.2',
        'PyYAML==6.0.2',
        'requests==2.32.3',
        's3transfer==0.11.1',
        'setuptools==75.8.0',
        'six==1.17.0',
        'typing_extensions==4.12.2',
        'tzdata==2024.2',
        'urllib3==2.3.0',
    ],
    entry_points={
        'console_scripts': [
            'lookerctl=src.lookerctl.lib.lookerctl:cli',  # Define entry point for command-line interface
        ],
    },
    package_data={
        '': ['config/*.ini', 'config/*.yaml'],  # Include configuration files in the package
    }
)
