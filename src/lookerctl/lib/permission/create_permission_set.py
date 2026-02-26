# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_existing_permission_set(sdk, permission_set_name):
    """
    Retrieves an existing permission set from Looker by name.

    Parameters:
        permission_set_name (str): The name of the permission set to retrieve.

    Process:
        - Fetches all permission sets using the Looker SDK.
        - Iterates through the permission sets to find one that matches the specified name.

    Returns:
        PermissionSet or None: The permission set object if found, or None if no match is found.

    Raises:
        looker_sdk.error.SDKError: If an error occurs while retrieving permission sets, an error message is printed, and None is returned.
    """
    try:
        existing_permission_sets = sdk.all_permission_sets()
        for permission_set in existing_permission_sets:
            if permission_set.name == permission_set_name:
                return permission_set
        return None
    except looker_sdk.error.SDKError as e:
        print(f"Error retrieving permission sets: {e}")
        return None


def create_permission_set(sdk, permission_set_data):
    """
    Creates a new permission set in Looker based on the provided permission set data.

    Parameters:
        permission_set_data (dict): Data containing the name and list of permissions for the permission set.

    Process:
        - Constructs a payload with the permission set name and permissions.
        - Calls the Looker SDK to create the permission set with the specified details.
        - Prints a success message or an error if creation fails.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during creation, an error message is printed to the console.
    """
    print(permission_set_data)
    try:
        permission_set_payload = {
            "name": permission_set_data['name'],
            "permissions": permission_set_data['permissions']
        }
        result = sdk.create_permission_set(body=permission_set_payload)
        print(f"Permission Set '{result.name}' created successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error creating permission set '{permission_set_data['name']}': {e}")


def update_permission_set(sdk, existing_permission_set, permission_set_data):
    """
    Updates an existing permission set in Looker based on provided data.

    Parameters:
        existing_permission_set (PermissionSet): The permission set object to be updated.
        permission_set_data (dict): Data containing updated permissions.

    Process:
        - Prepares an update payload with the permissions from the provided data.
        - Calls the Looker SDK to update the specified permission set.
        - Prints a success message or an error if update fails.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during update, an error message is printed to the console.
    """
    try:
        update_payload = {
            "permissions": permission_set_data['permissions']
        }

        result = sdk.update_permission_set(permission_set_id=existing_permission_set.id, body=update_payload)
        print(f"Permission Set '{result.name}' updated successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error updating permission set '{existing_permission_set.name}': {e}")


def process_permission_sets(sdk, yaml_data):
    """
    Processes permission sets from YAML configuration by creating or updating them in Looker.

    Parameters:
        yaml_data (dict): YAML data containing project and access control details.

    Process:
        - Retrieves permission sets from the YAML data.
        - Constructs permission set names prefixed with the project name.
        - For each permission set, checks if it exists; if so, updates it, otherwise creates a new one.

    Raises:
        ValueError: If the 'permission_sets' key is not found in YAML data.
    """
    permission_sets = yaml_data['access_control'].get('permission_sets')
    if not permission_sets:
        raise ValueError("YAML file does not contain 'permission_sets' key.")

    project_name = yaml_data['project']['name']

    for permission_set_data in permission_sets:
        permission_set_name = f"{project_name}_{permission_set_data['name']}"
        permission_set_data['name'] = permission_set_name
        existing_permission_set = get_existing_permission_set(sdk, permission_set_name)

        if existing_permission_set:
            update_permission_set(sdk, existing_permission_set, permission_set_data)
        else:
            create_permission_set(sdk, permission_set_data)
