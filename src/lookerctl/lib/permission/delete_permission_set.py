# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_permission_sets_starting_with_project_name(sdk, project_name):
    """
    Retrieves the names of permission sets in Looker that start with the specified project name.

    Parameters:
        project_name (str): The project name used as the prefix for permission sets.

    Process:
        - Fetches all permission sets using the Looker SDK.
        - Filters permission sets to include only those starting with the specified project name.
        - Removes the project name prefix from each permission set in the result list.
        - Prints the permission sets found or a message if none are found.

    Returns:
        list: A list of permission set names without the project name prefix.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during retrieval, an error message is printed, and an empty list is returned.
    """
    try:
        permission_sets = sdk.all_permission_sets()
        permission_sets_starting_with_project = [
            permission_set.name.replace(project_name + '_', "") for permission_set in permission_sets if permission_set.name.startswith(project_name)
        ]
        if permission_sets_starting_with_project:
            print(f"Permission sets starting with '{project_name}': {permission_sets_starting_with_project}")
        else:
            print(f"No permission sets found starting with '{project_name}'")
        return permission_sets_starting_with_project
    except looker_sdk.error.SDKError as e:
        print(f"Error fetching permission sets: {e}")
        return []


def delete_permission_set(sdk, permission_set_name):
    """
    Deletes a permission set in Looker by name.

    Parameters:
        permission_set_name (str): The name of the permission set to delete.

    Process:
        - Retrieves all permission sets and searches for the specified name.
        - If found, retrieves the permission set ID and calls the SDK to delete it.
        - Prints a success message if deletion is successful or an error if deletion fails.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during deletion, an error message is printed.
    """
    try:
        permission_set_id = None
        permission_sets = sdk.all_permission_sets()
        for permission_set in permission_sets:
            if permission_set.name == permission_set_name:
                permission_set_id = permission_set.id
                break

        if permission_set_id:
            sdk.delete_permission_set(permission_set_id=permission_set_id)
            print(f"Permission set '{permission_set_name}' deleted successfully!")
        else:
            print(f"Permission set '{permission_set_name}' not found.")
    except looker_sdk.error.SDKError as e:
        print(f"Error deleting permission set '{permission_set_name}': {e}")


def delete_unused_permission_sets(sdk, yaml_data):
    """
    Deletes permission sets in Looker that are not listed in the YAML configuration.

    Parameters:
        yaml_data (dict): YAML configuration data containing project and access control details.

    Process:
        - Collects permission set names from the YAML configuration.
        - Fetches Looker permission sets that start with the project name.
        - Identifies unused permission sets (not listed in YAML) and deletes each by name.

    Usage:
        This function is typically run at startup to clean up permission sets not specified in the YAML configuration.
    """
    project_name = yaml_data['project']['name']
    yaml_permission_set_names = []
    permission_sets = yaml_data['access_control'].get('permission_sets', [])

    if permission_sets:
        for permission_set in permission_sets:
            yaml_permission_set_names.append(permission_set['name'])

    looker_permission_set_names = get_permission_sets_starting_with_project_name(sdk, project_name)
    permission_sets_to_delete = [project_name + '_' + permission_set for permission_set in looker_permission_set_names if permission_set not in yaml_permission_set_names]

    for permission_set_name in permission_sets_to_delete:
        delete_permission_set(sdk, permission_set_name)
