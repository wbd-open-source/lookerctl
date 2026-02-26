# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import json
import looker_sdk
import boto3
from looker_sdk import models40 as mdls
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_db_credentials_from_secrets(sdk, secret_name, region_name):
    """
    Retrieves database credentials from AWS Secrets Manager.

    Parameters:
        secret_name (str): The name of the secret to retrieve.
        region_name (str): The AWS region where the secret is stored.

    Process:
        - Uses boto3 to connect to AWS Secrets Manager.
        - Retrieves the secret value and parses it as JSON if available.
        - Prints a message if 'SecretString' is not found or returns None if an error occurs.

    Returns:
        dict or None: The parsed secret as a dictionary if successful, or None if an error occurs.

    Raises:
        Exception: If an error occurs while fetching the secret, it is caught,
        printed, and None is returned.
    """
    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            secret = json.loads(response['SecretString'])
            return secret
        else:
            print(f"SecretString not found for {secret_name}")
            return None
    except TimeoutError as e:
        print(f"Timeout while fetching secret {secret_name}: {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        print(f"Invalid data or input while fetching secret {secret_name}: {e}")
        return None


def get_pdt_properties(yaml_data, secret_details):
    """
    Fetches PDT properties from yaml_data if PDT config exists.

    Returns:
        dict of PDT properties or empty dict
    """
    pdt_data = yaml_data['connections'].get('pdt')
    if not pdt_data:
        return {}

    pdt_context_override = convert_pdt_context_to_dict(pdt_data.get('pdt_context_override'), secret_details)

    return {
        "pdts_enabled": pdt_data.get('pdts_enabled'),
        "pdt_concurrency": pdt_data.get('concurrency'),
        "max_connections": pdt_data.get('max_connections'),
        "tmp_db_name": pdt_data.get('temp_db_name'),
        "maintenance_cron": pdt_data.get('maintenance_cron'),
        "always_retry_failed_builds": pdt_data.get('always_retry_failed_builds'),
        "pdt_api_control_enabled": pdt_data.get('pdt_api_control_enabled'),
        "ssl": pdt_data.get('ssl'),
        "verify_ssl": pdt_data.get('verify_ssl'),
        "sql_runner_precache_tables": pdt_data.get('cache'),
        "sql_writing_with_info_schema": pdt_data.get('sql_writing'),
        "pdt_context_override": pdt_context_override
    }


def create_databricks_connection(sdk, secret_details, yaml_data):
    if yaml_data['project']['name'] and yaml_data['connections']['name']:
        connection_name = yaml_data['project']['name'] + '_' + yaml_data['connections']['name']
    else:
        print("project_name or connection name is not provided")

    if 'token_value' not in secret_details:
        raise ValueError(f"token_value is missing in the secret: {yaml_data['secret_name']}")

    # Fetch PDT properties only if PDT key is present in YAML
    pdt_properties = get_pdt_properties(yaml_data, secret_details)

    connection = mdls.DBConnection(
        name=connection_name,
        dialect_name="databricks",
        host=yaml_data['connections'].get('host_name'),
        database=yaml_data['connections'].get('database'),
        username=yaml_data['connections'].get('user_name'),
        port=yaml_data['connections'].get('port'),
        password=secret_details['token_value'],
        jdbc_additional_params=yaml_data['connections'].get('jdbc_additional_params', ""),
        db_timezone=yaml_data['connections'].get('timezone', 'UTC'),
        query_timezone="UTC",
        pool_timeout=yaml_data['connections'].get('connection_timeout', 300),
        **pdt_properties  # Unpack PDT fields dynamically
    )

    try:
        sdk.create_connection(connection)
        test_connection_success(sdk, connection_name)
        print("Databricks connection created successfully!")
    except looker_sdk.error.SDKError as e:
        error_message = str(e)
        if 'already exists' in error_message:
            print(f"⚠️ Connection '{connection_name}' already exists. Testing existing connection...")
            test_connection_success(sdk, connection_name)
        else:
            print(f"Error creating Databricks connection: {e}")


def create_snowflake_connection(sdk, secret_details, yaml_data):
    """
    Creates a Snowflake connection in Looker based on provided secret details and YAML data.
    """
    if yaml_data['project']['name'] and yaml_data['connections']['name']:
        connection_name = yaml_data['project']['name'] + '_' + yaml_data['connections']['name']
    else:
        print("project_name or connection name is not provided")
        return

    pdt_properties = get_pdt_properties(yaml_data, secret_details)

    connection = mdls.DBConnection(
        name=connection_name,
        dialect_name="snowflake",
        host=yaml_data['connections'].get('host_name'),
        database=yaml_data['connections']['database'].upper(),
        username=yaml_data['connections'].get('login_name'),
        port=yaml_data['connections'].get('port'),
        password=secret_details['login_password'],
        jdbc_additional_params=yaml_data['connections'].get('jdbc_additional_params', ""),
        db_timezone=yaml_data['connections'].get('timezone', 'UTC'),
        query_timezone=yaml_data['connections'].get('query_timezone', 'UTC'),
        pool_timeout=yaml_data['connections'].get('connection_timeout', 300),
        **pdt_properties  # Inject PDT-related fields if available
    )

    try:
        sdk.create_connection(connection)
        test_connection_success(sdk, connection_name)
        print("Snowflake connection created successfully!")
    except looker_sdk.error.SDKError as e:
        error_message = str(e)
        if 'already exists' in error_message:
            print(f"⚠️ Connection '{connection_name}' already exists. Testing existing connection...")
            test_connection_success(sdk, connection_name)
        else:
            print(f"Error creating Snowflake connection: {e}")


def create_connection_based_on_dialect(region_name, sdk, yaml_data):
    """
    Creates a database connection in Looker based on the dialect specified in YAML data.

    Parameters:
        region_name (str): The AWS region where database credentials are stored in Secrets Manager.

    Process:
        - Retrieves the secret details using `get_db_credentials_from_secrets`.
        - Checks the dialect specified in YAML data and calls the appropriate function to create the connection.
        - Prints a message if the dialect is unsupported or if the secret retrieval fails.
    """
    secret_name = yaml_data['connections']['secret_name']
    secret = get_db_credentials_from_secrets(sdk, secret_name, region_name)
    if secret:
        if yaml_data['connections']['dialect_name']:
            dialect = yaml_data['connections']['dialect_name']
        else:
            print("Dailect name or connections is not available in the yaml provided.")
        if dialect == "snowflake":
            create_snowflake_connection(sdk, secret, yaml_data)
        elif dialect == "databricks":
            create_databricks_connection(sdk, secret, yaml_data)
        else:
            print(f"Unsupported dialect: {dialect}")
    else:
        print(f"Could not retrieve the secret: {secret_name}")


def test_connection_success(sdk, connection_name):
    """
    Tests a created database connection in Looker to ensure it is operational.

    Parameters:
        connection_name (str): The name of the connection to test.

    Process:
        - Calls the Looker SDK to test the connection.
        - Prints a success message if the connection test passes or an error message if it fails.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during the connection test, an error message is printed.
    """
    try:
        test_result = sdk.test_connection(connection_name, 'connect')  
        if test_result and test_result[0].status == 'success':
            print(f"Connection {connection_name} tested successfully!")
        else:
            print(f"Connection {connection_name} test failed: {test_result[0].message}")
    except looker_sdk.error.SDKError as e:
        print(f"Error testing connection {connection_name}: {e}")


def convert_pdt_context_to_dict(pdt_context, secret_details):
    """
    Converts pdt_context_override configuration into a dictionary.

    Parameters:
        pdt_context (dict): A dictionary containing the pdt_context_override settings from YAML.

    Returns:
        dict: A dictionary suitable for JSON serialization.
    """
    if not pdt_context:
        return None

    pdt_context_dict = {
        "context": "pdt",
        "host": pdt_context.get('host'),
        "port": pdt_context.get('port'),
        "username": pdt_context.get('username'),
        "password": secret_details['token_value'],
        "database": pdt_context.get('database'),
        "schema": pdt_context.get('schema'),
        "jdbc_additional_params": pdt_context.get('jdbc_additional_params', ""),
        "certificate": pdt_context.get('certificate', ""),
        "file_type": pdt_context.get('file_type', "")
    }

    return pdt_context_dict
