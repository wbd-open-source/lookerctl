# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_roles_starting_with_project_name(sdk, project_name):
    """
    Retrieves names of roles in Looker that start with the specified project name.

    Parameters:
        project_name (str): The project name used as the prefix for roles.

    Process:
        - Fetches all roles using the Looker SDK.
        - Filters roles to include only those starting with the specified project name.
        - Removes the project name prefix from each role name in the result list.
        - Prints the roles found or a message if none are found.

    Returns:
        list: A list of role names without the project name prefix that start with the specified project name.

    Raises:
        looker_sdk.error.SDKError: If an error occurs while retrieving roles, an error message is printed, and an empty list is returned.
    """
    try:
        roles = sdk.all_roles()
        roles_starting_with_project = [
            role.name.replace(project_name+'_', "") for role in roles if role.name.startswith(project_name)
        ]
        if roles_starting_with_project:
            print(f"Roles starting with '{project_name}': {roles_starting_with_project}")
        else:
            print(f"No roles found starting with '{project_name}'")
        return roles_starting_with_project
    except looker_sdk.error.SDKError as e:
        print(f"Error fetching roles: {e}")
        return []


def delete_role(sdk, role_name):
    """
    Deletes a role in Looker by name.

    Parameters:
        role_name (str): The name of the role to delete.

    Process:
        - Retrieves all roles and searches for the specified role name.
        - If found, retrieves the role ID and calls the SDK to delete it.
        - Prints a success message if deletion is successful or a message if the role is not found.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during deletion, an error message is printed.
    """
    try:
        role_id = None
        roles = sdk.all_roles()
        for role in roles:
            if role.name == role_name:
                role_id = role.id
                break

        if role_id:
            sdk.delete_role(role_id=role_id)
            print(f"Role '{role_name}' deleted successfully!")
        else:
            print(f"Role '{role_name}' not found.")
    except looker_sdk.error.SDKError as e:
        print(f"Error deleting role '{role_name}': {e}")


def delete_unused_roles(sdk, yaml_data):
    """
    Deletes roles in Looker that are not listed in the YAML configuration.

    Parameters:
        yaml_data (dict): YAML configuration data containing project and role details.

    Process:
        - Collects role names from the YAML configuration.
        - Fetches Looker roles that start with the project name.
        - Identifies unused roles (not listed in YAML) and deletes each by name.

    Usage:
        This function is typically run at startup to clean up roles not specified in the YAML configuration.
    """
    project_name = yaml_data['project']['name']
    yaml_role_names = []
    role_sets = yaml_data['access_control'].get('roles', [])

    for role_set in role_sets:
        yaml_role_names.append(role_set['name'])

    project_name = yaml_data['project']['name']

    looker_role_names = get_roles_starting_with_project_name(sdk, project_name)

    roles_to_delete = [project_name+'_'+role for role in looker_role_names if role not in yaml_role_names]

    for role_name in roles_to_delete:
        delete_role(sdk, role_name)
