# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
from looker_sdk import models40 as mdls
from looker_sdk.error import SDKError
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def create_groups_from_yaml(sdk, groups):
    """
    Creates Looker groups from a list of group configurations.
    """
    for group in groups:
        try:
            body = mdls.WriteGroup(
                name=group["name"]
            )
            created = sdk.create_group(body=body)
            print(f"Created group '{created.name}' with ID {created.id}")
        except SDKError as e:
            print(f"Error creating group '{group['name']}': {e}")
