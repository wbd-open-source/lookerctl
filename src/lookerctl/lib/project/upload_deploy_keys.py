# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import requests
import os

def add_deploy_key_to_github(repo_owner, repo_name, title, public_key, read_only=True):
    """
    Adds a deploy key to the specified GitHub repository.

    Parameters:
        repo_owner (str): GitHub organization or user name.
        repo_name (str): GitHub repository name.
        title (str): Name of the deploy key.
        public_key (str): The SSH public key to add.
        read_only (bool): True to allow read-only access, False for write access.

    Returns:
        dict: GitHub API response (success or error).
    """
    token = os.getenv('GITHUB_TOKEN')
    print(token)
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/keys"
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}", 
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "title": title,
        "key": public_key,
        "read_only": read_only
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    if response.status_code == 201:
        print(" Deploy key added successfully to GitHub.")
    else:
        print(f" Failed to add deploy key. {response.status_code}: {response.text}")

    return response.json()
