# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_model_set_ids_starting_with_project_name(sdk, project_name):
    """
    Retrieves IDs and names of model sets in Looker that start with the specified project name, excluding the default model set.

    Parameters:
        project_name (str): The project name used as the prefix for model sets.

    Process:
        - Fetches all model sets using the Looker SDK.
        - Filters model sets to include only those starting with the project name.
        - Excludes the default model set from the results.
        - Prints model sets found or a message if none are found.

    Returns:
        dict: A dictionary of model set IDs and their corresponding names without the project name prefix.

    Raises:
        looker_sdk.error.SDKError: If an error occurs while retrieving model sets, an error message is printed, and an empty dictionary is returned.
    """
    try:
        model_sets = sdk.all_model_sets()
        model_sets_starting_with_project = {
            model_set.id: model_set.name.replace(project_name + '_', "") for model_set in model_sets if model_set.name.startswith(project_name)
        }
        model_sets_starting_with_project = {k: v for k, v in model_sets_starting_with_project.items() if v != 'default_model_set'}

        if model_sets_starting_with_project:
            print(f"Model sets starting with '{project_name}': {model_sets_starting_with_project}")
        else:
            print(f"No model sets found starting with '{project_name}'")
        return model_sets_starting_with_project
    except looker_sdk.error.SDKError as e:
        print(f"Error retrieving model sets: {e}")
        return {}


def delete_model_set_by_id(sdk, model_set_id):
    """
    Deletes a model set in Looker by its ID.

    Parameters:
        model_set_id (int): The ID of the model set to delete.

    Process:
        - Calls the Looker SDK to delete the specified model set by ID.
        - Prints a success message upon deletion or an error if deletion fails.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during deletion, an error message is printed to the console.
    """
    try:
        sdk.delete_model_set(model_set_id=model_set_id)
        print(f"Model Set with ID '{model_set_id}' deleted successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error deleting model set with ID '{model_set_id}': {e}")


def delete_unused_model_sets(sdk, yaml_data):
    """
    Deletes model sets in Looker that are not listed in the YAML configuration.

    Parameters:
        yaml_data (dict): YAML configuration data containing project and model set details.

    Process:
        - Collects model set names from YAML configuration under access control.
        - Fetches Looker model sets that start with the project name.
        - Identifies unused model sets (not listed in YAML) and deletes each by ID.

    Usage:
        This function is typically run at startup to clean up model sets not specified in the YAML configuration.
    """
    yaml_model_set_names = [model_set_data['name'] for model_set_data in yaml_data['access_control'].get('model_set', [])]
    project_name = yaml_data['project']['name']
    looker_model_sets = get_model_set_ids_starting_with_project_name(sdk, project_name)
    model_sets_to_delete = [model_set_id for model_set_id, model_set_name in looker_model_sets.items() if model_set_name not in yaml_model_set_names]
    for model_set_id in model_sets_to_delete:
        delete_model_set_by_id(sdk, model_set_id)
