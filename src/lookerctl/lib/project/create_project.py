# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import requests
import looker_sdk
from looker_sdk import models40

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from . import github_integration # noqa: E402


def add_deploy_key_to_github(repo_owner, repo_name, title, public_key, read_only=True):
    """
    Adds a deploy key to the specified GitHub repository.
    """
    token = os.getenv('LOOKER_ENV_GITHUB_PAT')
    if not token:
        raise EnvironmentError("GITHUB_TOKEN not set in environment variables.")

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/keys"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "title": title,
        "key": public_key,
        "read_only": read_only
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    if response.status_code == 201:
        print("Deploy key added successfully to GitHub.")
    else:
        print(f"Failed to add deploy key. {response.status_code}: {response.text}")
        response.raise_for_status()

    return response.json()


def configure_git_for_project(sdk, yaml_data, project_name, branch):
    """
    Configures Git integration for the specified Looker project.
    """
    deploy_key = sdk.create_git_deploy_key(project_name)
    github_config = yaml_data['project']

    add_deploy_key_to_github(
        repo_owner=github_config['owner'],
        repo_name=github_config['repo_name'],
        title=github_config.get('title', f"Looker Deploy Key - {project_name}"),
        public_key=deploy_key,
        read_only=github_config.get('read_only', False)
    )

    sdk.update_project(project_name, models40.WriteProject(
        git_remote_url=github_config['git_remote_url'],
        git_service_name=github_config.get('git_service_name', 'github'),
        # git_production_branch_name=branch  # Uncomment if needed
    ))
    print(f"Git configuration updated for project '{project_name}'.")


def create_project(sdk, yaml_data, env):
    """
    Creates a new Looker project and configures Git integration.
    """
    try:
        project_name = yaml_data['project']['name']
        if env == "dev":
            branch = "develop"
        elif env == "prod":
            branch = "main"
        else:
            raise ValueError(f"Unsupported environment '{env}'. Use 'dev' or 'prod'.")
    except KeyError as e:
        raise KeyError(f"Missing key in YAML data: {e}") from None

    try:
        sdk.update_session(models40.WriteApiSession(workspace_id="dev"))

        project = sdk.create_project(models40.WriteProject(name=project_name))
        print(f"Project '{project_name}' created successfully.")

        configure_git_for_project(sdk, yaml_data, project_name, branch)

        return project

    except looker_sdk.error.SDKError as e:
        error_message = str(e)
        if 'already exists' in error_message:
            print(f"Project '{project_name}' already exists. Skipping creation.")
            existing_projects = sdk.all_projects()
            for project in existing_projects:
                if project.name == project_name:
                    configure_git_for_project(sdk, yaml_data, project_name, branch)
                    return project
            print(f"Project '{project_name}' exists but not found in list.")
            return None
        else:
            print(f"SDKError: {error_message}")
            raise

    except Exception as e:
        print(f"Unhandled error: {e}")
        raise
