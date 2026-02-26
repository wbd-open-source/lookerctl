# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root
# for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def create_model(sdk, model_name, label, yaml_data):
    """
    Creates a LookML model in Looker with the specified name and label.

    Parameters:
        sdk (Looker40SDK): The Looker SDK instance.
        model_name (str): The name of the model to be created.
        label (str): The label for the model.
        yaml_data (dict): Parsed YAML data containing project info.

    Returns:
        dict or None: The created or existing model dictionary, or None if
        failed.
    """
    try:
        model = sdk.create_lookml_model({
            'name': model_name,
            'label': label,
            'project_name': yaml_data['project']['name']
        })
        print(f"Model '{model_name}' created successfully!")
        return model

    except looker_sdk.error.SDKError as e:
        error_message = str(e)
        if 'already exists' in error_message:
            print(f"Model '{model_name}' already exists."
                  " Fetching existing model...")
            try:
                existing_model = sdk.lookml_model(model_name)
                print(f"Found existing model '{model_name}'")
                return existing_model
            except (KeyError, ValueError, TypeError) as e:
                print(
                    f"Invalid data or input while fetching model"
                    f" '{model_name}': {e}"
                    )
                return None
            except ConnectionError as e:
                print(f"Network error while contacting Looker SDK for model"
                      f" '{model_name}': {e}")
                return None
            except TimeoutError as e:
                print(f"Timeout while fetching model '{model_name}': {e}")
                return None
        else:
            print(f"Error creating model '{model_name}': {e}")
            raise


def create_models_from_yaml(sdk,yaml_data):
    """
    Creates multiple LookML models from YAML configuration data.

    Parameters:
        yaml_data (dict): YAML data containing project and model details.

    Process:
        - Retrieves the project name from the YAML data.
        - Iterates over each model in the 'model' section of YAML data.
        - Constructs the full model name by combining the project name and model name.
        - Calls `create_model` for each model with the constructed name and label.

    Usage:
        This function is typically called once at runtime to create all models defined in the YAML configuration.
    """
    project_name = yaml_data['project']['name']
    model_sets = yaml_data.get('model', [])

    for model_set in model_sets:
        model_name = model_set['name']
        label = model_set.get('label', 'Default Label')
        full_model_name = f"{project_name}_{model_name}"
        create_model(sdk, full_model_name, label, yaml_data)
