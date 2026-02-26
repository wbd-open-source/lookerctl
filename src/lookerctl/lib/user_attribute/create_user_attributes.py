# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
from looker_sdk import models40 as mdls
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_existing_user_attribute(sdk, attribute_name):
    """
    Retrieves an existing user attribute in Looker by name.

    Parameters:
        attribute_name (str): The name of the user attribute to retrieve.

    Process:
        - Fetches all user attributes using the Looker SDK.
        - Searches for an attribute that matches the specified name.

    Returns:
        UserAttribute or None: The user attribute object if found, or None if not found or an error occurs.
    """
    try:
        existing_attributes = sdk.all_user_attributes()
        for attribute in existing_attributes:
            if attribute.name == attribute_name:
                return attribute
        return None
    except looker_sdk.error.SDKError as e:
        print(f"Error retrieving user attributes: {e}")
        return None


def create_user_attribute(sdk, attribute_data, prefix):
    """
    Creates a new user attribute in Looker with a specified prefix.

    Parameters:
        sdk (Looker40SDK): Looker SDK instance.
        attribute_data (dict): Data containing the attribute's name, label, type, and other settings.
        prefix (str): The prefix to prepend to the attribute name.

    Returns:
        UserAttribute or None: The created or existing user attribute object if successful, or None if failed.
    """
    attribute_name = f"{prefix}_{attribute_data['name']}"
    try:
        attribute_payload = {
            "name": attribute_name,
            "label": attribute_data['label'],
            "type": attribute_data['type'],
            "default_value": attribute_data['default_value'],
            "value_is_hidden": attribute_data['value_is_hidden'],
            "user_can_view": attribute_data['user_can_view'],
            "user_can_edit": attribute_data['user_can_edit']
        }
        result = sdk.create_user_attribute(body=attribute_payload)
        print(f"User attribute '{result.name}' created successfully!")
        return result

    except looker_sdk.error.SDKError as e:
        error_message = str(e)
        if 'already exists' in error_message:
            print(f"⚠️ User attribute '{attribute_name}' already exists. Fetching existing attribute...")
            try:
                existing = get_existing_user_attribute(sdk, attribute_name)
                if existing:
                    print(f"Found existing user attribute '{attribute_name}'")
                    return existing
                else:
                    print(f"Attribute '{attribute_name}' exists but could not be found.")
                    return None
            except Exception as fetch_error:
                print(f"Error fetching existing attribute: {fetch_error}")
                return None
            except (KeyError, TypeError, ValueError) as e:
                print(f"Data issue while fetching existing attribute '{attribute_name}': {e}")
                return None
        else:
            print(f"Error creating user attribute '{attribute_name}': {e}")
            raise


def update_user_attribute(sdk, existing_attribute, attribute_data, prefix):
    """
    Updates an existing user attribute in Looker based on provided data.

    Parameters:
        existing_attribute (UserAttribute): The attribute to update.
        attribute_data (dict): Data containing updated settings for the attribute.
        prefix (str): The prefix to prepend to the attribute name (not used in this function but matches signature).

    Process:
        - Constructs an update payload with the attribute details and calls the Looker SDK to update it.
    """
    try:
        update_payload = {
            "label": attribute_data['label'],
            "type": attribute_data['type'],
            "default_value": attribute_data['default_value'],
            "value_is_hidden": attribute_data['value_is_hidden'],
            "user_can_view": attribute_data['user_can_view'],
            "user_can_edit": attribute_data['user_can_edit']
        }
        result = sdk.update_user_attribute(user_attribute_id=existing_attribute.id, body=update_payload)
        print(f"User attribute '{result.name}' updated successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error updating user attribute '{existing_attribute.name}': {e}")


def assign_user_attribute_to_groups(sdk, attribute_id, group_values):
    """
    Assigns specified values of a user attribute to groups.

    Parameters:
        attribute_id (int): The ID of the user attribute to assign values to.
        group_values (list): List of dictionaries, each containing a group name and a value.

    Process:
        - Searches for each group by name and creates a list of values to assign.
        - Calls the Looker SDK to assign each group its specific attribute value.
    """
    try:
        group_value_objects = []
        for group_value in group_values:
            group = sdk.search_groups(name=group_value['group_name'])
            if group:
                group_id = group[0].id
                group_value_object = mdls.UserAttributeGroupValue(
                    group_id=group_id,
                    value=group_value['value']
                )
                group_value_objects.append(group_value_object)
            else:
                print(f"Group '{group_value['group_name']}' not found. Skipping assignment.")
        if group_value_objects:
            sdk.set_user_attribute_group_values(
                user_attribute_id=attribute_id,
                body=group_value_objects
            )
            print(f"Assigned values to groups for user attribute {attribute_id}.")
        else:
            print(f"No valid groups found to assign values for user attribute {attribute_id}.")
    except looker_sdk.error.SDKError as e:
        print(f"Error assigning values to groups: {e}")


def process_user_attributes(sdk, yaml_data):
    """
    Processes user attributes in the YAML configuration by creating or updating them in Looker.

    Parameters:
        yaml_data (dict): YAML data containing project and access control details.

    Process:
        - Retrieves project name and user attributes from YAML data.
        - Checks if each attribute exists; if so, updates it, otherwise creates a new one.
        - Assigns attribute values to specified groups.
    """
    ATTRIBUTE_PREFIX = yaml_data['project']['name']
    project_name = yaml_data.get('project', {}).get('name', ATTRIBUTE_PREFIX)
    user_attributes = yaml_data.get('access_control', {}).get('user_attributes', [])
    if not user_attributes:
        return "No user attributes found in YAML data."

    # Iterate over each user attribute provided in the configuration
    for attribute_data in user_attributes:
        # Prefix the attribute name with the project name to create a unique identifier
        prefixed_name = f"{project_name}_{attribute_data['name']}"

        # Attempt to retrieve an existing user attribute by its prefixed name
        existing_attribute = get_existing_user_attribute(sdk, prefixed_name)

        # If the attribute already exists, update it with the new data
        if existing_attribute:
            update_user_attribute(sdk, existing_attribute, attribute_data, project_name)
            attribute_id = existing_attribute.id
        else:
            # If the attribute does not exist, create a new one and store its ID
            new_attribute = create_user_attribute(sdk, attribute_data, project_name)
            attribute_id = new_attribute.id if new_attribute else None

        # If the attribute ID is valid and there are group values specified, assign these values to the groups
        if attribute_id and 'group_values' in attribute_data:
            assign_user_attribute_to_groups(sdk, attribute_id, attribute_data['group_values'])
