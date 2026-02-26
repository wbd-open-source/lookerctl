# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
from time import time

import looker_sdk.error
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_existing_model_set(sdk, model_set_name):
    """
    Retrieves an existing model set from Looker by name.

    Parameters:
        model_set_name (str): The name of the model set to retrieve.

    Returns:
        ModelSet or None: The model set object if found, or None if no match is found.

    Raises:
        looker_sdk.error.SDKError: Prints an error message if there is an issue retrieving model sets.
    """
    try:
        existing_model_sets = sdk.all_model_sets()
        for ms in existing_model_sets:
            if ms.name == model_set_name:
                return ms
        return None
    except looker_sdk.error.SDKError as e:
        print(f"Error retrieving model sets: {e}")
        return None


def prepend_project_name_to_models(sdk, models, yaml_data):
    """
    Prepends the project name from YAML data to each model in a list of models.

    Parameters:
        models (list): List of model names.

    Returns:
        list: List of model names prefixed with the project name.
    """
    if yaml_data['project']['name']:
        project_name = yaml_data['project']['name']
    else:
        print("Project name is missing in the Yaml.")
    return [f"{project_name}_{model}" for model in models]


def create_model_set(sdk, model_set_data, yaml_data):
    """
    Creates a new model set in Looker based on provided model set data.
    """
    try:
        prefixed_models = prepend_project_name_to_models(sdk, model_set_data.get('models', []), yaml_data)
        custom_models = model_set_data.get('custom_models', [])
        model_names = prefixed_models + custom_models
        print("Final models:", model_names)

        model_set_payload = {
            "name": f"{yaml_data['project']['name']}_{model_set_data['name']}",
            "models": model_names
        }
        result = sdk.create_model_set(body=model_set_payload)
        print(f"Model Set '{result.name}' created successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error creating model set '{model_set_data['name']}': {e}")


def update_model_set(sdk, existing_model_set, model_set_data, yaml_data):
    """
    Updates an existing model set in Looker based on provided data.
    """
    try:
        prefixed_models = prepend_project_name_to_models(sdk, model_set_data.get('models', []), yaml_data)
        custom_models = model_set_data.get('custom_models', [])

        model_names = prefixed_models + custom_models
        print("Final models:", model_names)

        update_payload = {
            "models": model_names
        }

        if model_set_data.get('rename_model', False) and model_set_data.get('new_name'):
            update_payload["name"] = f"{yaml_data['project']['name']}_{model_set_data['new_name']}"

        result = sdk.update_model_set(model_set_id=existing_model_set.id, body=update_payload)
        print(f"Model Set '{result.name}' updated successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error updating model set '{existing_model_set.name}': {e}")


def process_model_sets(sdk, yaml_data):
    """
    Processes model sets from YAML configuration by creating or updating them in Looker.

    Parameters:
        yaml_data (dict): YAML data containing project and access control details.

    Raises:
        ValueError: If the 'model_set' key is not found in YAML data.
    """
    model_sets = yaml_data['access_control'].get('model_set')
    if not model_sets:
        raise ValueError("YAML file does not contain 'model_set' key.")

    for model_set_data in model_sets:
        print("model_set_data", model_set_data)
        model_set_name = f"{yaml_data['project']['name']}_{model_set_data['name']}"
        existing_model_set = get_existing_model_set(sdk, model_set_name)

        if existing_model_set:
            update_model_set(sdk, existing_model_set, model_set_data, yaml_data)
        else:
            create_model_set(sdk, model_set_data, yaml_data)


def create_default_model_set(sdk, yaml_data, max_retries=3):
    """
    Creates or updates a default model set in Looker with all models starting with the project name.

    Process:
        - Retrieves all models with the project name prefix.
        - Checks if the default model set exists, then updates or creates it based on model presence.

    Raises:
        looker_sdk.error.SDKError: Prints an error if there is an issue creating or updating the model set.
    """
    try:
        project_name = yaml_data['project']['name']
        default_model_set_name = f"{project_name}_default_model_set"
        for attempt in range(max_retries):
            try:
                all_models = [
                    model.name for model in sdk.all_lookml_models()
                    if model.name.startswith(project_name)
                ]
                break
            except looker_sdk.error.SDKError as e:
                print(f"Attempt {attempt + 1} failed to fetch models: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    raise

        models_with_project_name = [model.replace(f"{project_name}_", "") for model in all_models]
        existing_model_set = get_existing_model_set(sdk, default_model_set_name)

        if existing_model_set:
            existing_models = set(existing_model_set.models)
            new_models = set(models_with_project_name)

            if new_models != existing_models:
                print("New models detected. Updating the default model set.")
                update_model_set(sdk, existing_model_set, {"models": list(new_models)}, yaml_data)
            else:
                print("No new models to add. Default model set is up to date.")
        else:
            print("Default model set does not exist. Creating a new one.")
            model_set_payload = {
                "name": default_model_set_name,
                "models": models_with_project_name
            }
            create_model_set(sdk, model_set_payload, yaml_data)

    except looker_sdk.error.SDKError as e:
        print(f"Error creating or updating the default model set: {e}")
    except (KeyError, ValueError, TypeError) as e:
        print(f"Invalid data or input while creating/updating the model set: {e}")
    except ConnectionError as e:
        print(f"Network error while communicating with Looker: {e}")
    except TimeoutError as e:
        print(f"Request timed out while creating/updating the model set: {e}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")
