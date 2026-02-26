# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_models_starting_with_project_name(sdk,project_name):
    """
    Fetches all LookML models from Looker that start with the specified project name.

    Parameters:
        project_name (str): The project name to match at the start of each model name.

    Process:
        - Retrieves all LookML models using the SDK.
        - Filters models to include only those whose names start with the specified project name.
        - Strips the project name prefix from each model name in the result list.

    Returns:
        list: A list of model names without the project name prefix that start with the specified project name.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during model retrieval, it is printed and an empty list is returned.
    """
    try:
        models = sdk.all_lookml_models()
        models_starting_with_project = [
            model.name.replace(project_name+'_', "") for model in models if model.name.startswith(project_name)
        ]
        if models_starting_with_project:
            print(f"Models starting with '{project_name}': {models_starting_with_project}")
        else:
            print(f"No models found starting with '{project_name}'")
        return models_starting_with_project
    except looker_sdk.error.SDKError as e:
        print(f"Error fetching models: {e}")
        return []


def delete_model(sdk, model_name):
    """
    Deletes a LookML model from Looker by name.

    Parameters:
        model_name (str): The name of the model to delete.

    Process:
        - Calls the Looker SDK to delete the specified model.
        - Prints a success message upon successful deletion or an error if deletion fails.

    Raises:
        looker_sdk.error.SDKError: If an error occurs during model deletion, it is printed to the console.
    """
    try:
        sdk.delete_lookml_model(lookml_model_name=model_name)
        print(f"Model '{model_name}' deleted successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error deleting model '{model_name}': {e}")


def delete_unused_models(sdk, yaml_data):
    """
    Deletes models from Looker that are not listed in the YAML configuration.

    Parameters:
        yaml_data (dict): YAML configuration data containing project and model details.

    Process:
        - Collects model names from the YAML configuration.
        - Fetches model names in Looker that start with the project name.
        - Compares YAML model names to Looker model names to identify unused models.
        - Calls `delete_model` to delete each unused model.

    Usage:
        This function is typically run once at startup to clean up models not specified in the YAML configuration.
    """
    yaml_model_names = []
    model_sets = yaml_data.get('model', [])

    for model_set in model_sets:
        yaml_model_names.append(model_set['name'])
    project_name = yaml_data['project']['name']
    looker_model_names = get_models_starting_with_project_name(sdk, project_name)
    models_to_delete = [project_name+'_'+model for model in looker_model_names if model not in yaml_model_names]
    for model_name in models_to_delete:
        delete_model(sdk, model_name)
