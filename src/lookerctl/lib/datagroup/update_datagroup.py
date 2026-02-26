# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import looker_sdk
import os
import sys
import time
from looker_sdk import models40 as mdls
from looker_sdk.error import SDKError


def get_datagroup_id_by_name(sdk, datagroupname, model_name):
    """
    Retrieves the ID of a datagroup by matching its name and model_name.

    Parameters:
        sdk (looker_sdk.SDK): Initialized Looker SDK object.
        datagroupname (str): Name of the datagroup.
        model_name (str): Name of the model the datagroup belongs to.

    Returns:
        str or None: The datagroup ID if found, else None.
    """
    datagroups = sdk.all_datagroups()
    for datagroup in datagroups:
        if datagroup.name == datagroupname and datagroup.model_name == model_name:
            print(f"Found datagroup ID: {datagroup.id}")
            return datagroup.id
    print("Datagroup not found.")
    return None


def trigger_datagroup(sdk, datagroupname, model_name):
    """
    Triggers a Looker datagroup refresh by setting stale_before and triggered_at.

    Parameters:
        sdk (looker_sdk.SDK): Initialized Looker SDK object.
        datagroupname (str): Name of the datagroup to trigger.
        model_name (str): Name of the model the datagroup belongs to.

    Returns:
        mdls.Datagroup or None: The updated datagroup object or None on error.
    """
    datagroup_id = get_datagroup_id_by_name(sdk, datagroupname, model_name)
    if not datagroup_id:
        return None

    update_body = mdls.WriteDatagroup(
        stale_before=get_current_epoch_time(),
        triggered_at=get_current_epoch_time() - 60
    )

    try:
        response = sdk.update_datagroup(
            datagroup_id=datagroup_id,
            body=update_body
        )
        print("Datagroup updated successfully:", response)
        return response
    except SDKError as e:
        print(f"Error updating datagroup {datagroup_id}: {e}")
        return None


def get_current_epoch_time():
    """
    Returns the current epoch time in seconds.

    Returns:
        int: Current epoch time.
    """
    return int(time.time())
