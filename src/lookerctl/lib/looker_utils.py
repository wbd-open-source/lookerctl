# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import os
import configparser
import tempfile
import looker_sdk
from looker_sdk import error


def get_sdk(env):
    """
    Initializes the Looker SDK using configuration details stored temporarily in an .ini file.
    Retrieves API connection details from environment variables and writes them to a temporary file used for SDK initialization.

    Parameters:
        env (str): The environment for which the SDK is initialized. Currently not used but could be utilized for environment-specific configurations.

    Process:
        - Retrieves API connection details from environment variables.
        - Creates a temporary .ini file with these details.
        - Initializes the Looker SDK using this .ini file.
        - Attempts a test API call to verify successful initialization.
        - Deletes the temporary .ini file.

    Returns:
        looker_sdk.client40.Client or None: The initialized SDK client if successful, None if there is an error.
    """
    base_url = os.getenv('LOOKER_ENV_LOOKER_HOSTNAME')
    client_id = os.getenv('LOOKER_ENV_CLIENT_ID')
    client_secret = os.getenv('LOOKER_ENV_CLIENT_SECRET')
    api_version = 4.0
    verify_ssl = True

    data = {
        'Looker': {
            'base_url': str(base_url),
            'client_id': str(client_id),
            'client_secret': str(client_secret),
            'api_version': str(api_version),
            'verify_ssl': str(verify_ssl)
        }
    }

    config = configparser.ConfigParser()
    for section, values in data.items():
        config.add_section(section)
        for key, value in values.items():
            config.set(section, key, value)

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.ini') as temp_file:
        config.write(temp_file)
        temp_file_path = temp_file.name

    try:
        sdk = looker_sdk.init40(config_file=temp_file_path)
        test_users = sdk.all_users(fields="id")
        if not test_users:
            print("Failed to initialize SDK or fetch data. Check API settings.")
            return None
        print("SDK initialized successfully with test user fetch.")
        return sdk
    except error.SDKError as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        os.remove(temp_file_path)
        print(f"Temporary .ini file deleted: {temp_file_path}")
