# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_model_set_id_by_name(sdk, model_set_name):
    """
    Retrieves the ID of a model set in Looker by name.

    Parameters:
        model_set_name (str): The name of the model set to retrieve.

    Process:
        - Fetches all model sets using the Looker SDK.
        - Iterates through the model sets to find one that matches the specified name.

    Returns:
        int or None: The model set ID if found, or None if no match is found.

    Raises:
        looker_sdk.error.SDKError: If an error occurs while retrieving model sets, an error message is printed, and None is returned.
    """
    try:
        model_sets = sdk.all_model_sets()
        for model_set in model_sets:
            if model_set.name == model_set_name:
                return model_set.id
        print(f"Model set '{model_set_name}' not found.")
        return None
    except looker_sdk.error.SDKError as e:
        print(f"Error retrieving model sets: {e}")
        return None


def get_permission_set_id_by_name(sdk, permission_set_name):
    """
    Retrieves the ID of a permission set in Looker by name.

    Parameters:
        permission_set_name (str): The name of the permission set to retrieve.

    Process:
        - Fetches all permission sets using the Looker SDK.
        - Iterates through the permission sets to find one that matches the specified name.

    Returns:
        int or None: The permission set ID if found, or None if no match is found.

    Raises:
        looker_sdk.error.SDKError: If an error occurs while retrieving permission sets, an error message is printed, and None is returned.
    """
    try:
        permission_sets = sdk.all_permission_sets()
        for permission_set in permission_sets:
            if permission_set.name == permission_set_name:
                return permission_set.id
        print(f"Permission set '{permission_set_name}' not found.")
        return None
    except looker_sdk.error.SDKError as e:
        print(f"Error retrieving permission sets: {e}")
        return None


def get_existing_role(sdk, role_name):
    """
    Retrieves an existing role from Looker by name.

    Parameters:
        role_name (str): The name of the role to retrieve.

    Process:
        - Fetches all roles using the Looker SDK.
        - Searches for a role that matches the specified name.

    Returns:
        Role or None: The role object if found, or None if no match is found.

    Raises:
        looker_sdk.error.SDKError: If an error occurs while retrieving roles, an error message is printed, and None is returned.
    """
    try:
        existing_roles = sdk.all_roles()
        for role in existing_roles:
            if role.name == role_name:
                return role
        return None
    except looker_sdk.error.SDKError as e:
        print(f"Error retrieving roles: {e}")
        return None


def create_role(sdk, role_data):
    """
    Creates a new role in Looker based on provided role data.

    Parameters:
        role_data (dict): Data containing role name, permission set ID, and model set ID.

    Process:
        - Constructs a payload with the role name, permission set ID, and model set ID.
        - Calls the Looker SDK to create the role.
        - Prints a success message if creation is successful or an error if creation fails.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during creation, an error message is printed.
    """
    try:
        role_payload = {
            "name": role_data['name'],
            "permission_set_id": role_data['permission_set_id'],
            "model_set_id": role_data['model_set_id']
        }
        result = sdk.create_role(body=role_payload)
        print(f"Role '{result.name}' created successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error creating role '{role_data['name']}': {e}")


def update_role(sdk, existing_role, role_data):
    """
    Updates an existing role in Looker based on provided role data.

    Parameters:
        existing_role (Role): The role object to be updated.
        role_data (dict): Data containing updated permission set ID, model set ID, and optionally a new name.

    Process:
        - Constructs an update payload with the permission set ID and model set ID.
        - If a rename flag and new name are provided, includes the new name in the update payload.
        - Calls the Looker SDK to update the specified role.
        - Prints a success message if the update is successful or an error if the update fails.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during the update, an error message is printed.
    """
    try:
        update_payload = {
            "permission_set_id": role_data['permission_set_id'],
            "model_set_id": role_data['model_set_id']
        }
        if role_data.get('rename_flag', False) and role_data.get('new_name'):
            update_payload["name"] = role_data['new_name']

        result = sdk.update_role(role_id=existing_role.id, body=update_payload)
        print(f"Role '{result.name}' updated successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error updating role '{existing_role.name}': {e}")


def process_roles(sdk, env, yaml_data):
    """
    Processes roles from YAML configuration by creating or updating them in Looker.

    Parameters:
        yaml_data (dict): YAML data containing project, access control, and role details.

    Process:
        - Validates the presence of the project name and access control roles in YAML data.
        - For each role, constructs a full role name with the project prefix.
        - Retrieves associated model set and permission set IDs by name.
        - Checks if the role exists in Looker; if so, updates it, otherwise creates a new one.

    Raises:
        ValueError: If required keys ('project', 'name', 'access_control', 'roles') are missing in YAML data.
    """
    access_control = yaml_data.get('access_control')
    project_name = yaml_data.get('project', {}).get('name', '')

    if not project_name:
        raise ValueError("YAML file does not contain 'project' key or 'name' under 'project'.")
    if not access_control or not access_control.get('roles'):
        raise ValueError("YAML file does not contain 'access_control' or 'roles' key.")

    roles = access_control['roles']

    for role_data in roles:
        role_name = f"{project_name}_{role_data['name']}"
        modelset_name = yaml_data['project']['name']+'_'+role_data['model_set_name']
        model_set_id = get_model_set_id_by_name(sdk, modelset_name)

        if model_set_id is None:
            print(f"Model set '{role_data['model_set_name']}' not found for role '{role_name}'. Skipping role.")
            continue

        role_data['model_set_id'] = model_set_id
        if env == "dev":
            default_sets = ["Deployment Developer", "User", "Viewer"]
        elif env == "prod":
            default_sets = ["Viewer", "User", "Contributer"]
        if role_data['permission_set_name'] not in default_sets:
            permissions_set_name = yaml_data['project']['name']+'_'+role_data['permission_set_name']
        else:
            permissions_set_name = role_data['permission_set_name']
        permission_set_id = get_permission_set_id_by_name(sdk, permissions_set_name)

        if permission_set_id is None:
            print(f"Permission set '{role_data['permission_set_name']}' not found for role '{role_name}'. Skipping role.")
            continue

        role_data['permission_set_id'] = permission_set_id
        role_data['name'] = role_name
        existing_role = get_existing_role(sdk, role_name)

        if existing_role:
            update_role(sdk, existing_role, role_data)
        else:
            create_role(sdk, role_data)
