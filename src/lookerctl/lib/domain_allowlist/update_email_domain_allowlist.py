# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
from looker_sdk import models40 as mdls
from looker_sdk.error import SDKError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def update_domain_allowlist(sdk, yaml_data):
    """
    Updates the Looker email domain allowlist with new domains specified in the YAML configuration.

    This function:
    - Retrieves the current email domain allowlist setting from Looker.
    - Merges it with the list of new domains provided in the 'email_domain_allowlist' field of the YAML config.
    - Deduplicates and sorts the combined list.
    - Updates the allowlist in Looker only if there are changes.
    - Prints appropriate messages for each outcome.

    Parameters:
        sdk (looker_sdk.sdk.api40.methods.Looker40SDK): An initialized Looker SDK client object.
        yaml_data (dict): A dictionary parsed from a YAML config file containing the key 
                          'email_domain_allowlist' with a list of domains to be added.

    Returns:
        None
    """
    try:
        current_setting = sdk.get_setting(fields="email_domain_allowlist")
        existing_domains = current_setting.email_domain_allowlist or []

        new_domains = yaml_data.get("email_domain_allowlist", [])
        if not new_domains:
            print("No new domains found in YAML config. Nothing to update.")
            return

        combined_domains = sorted(set(existing_domains + new_domains))

        if sorted(existing_domains) == combined_domains:
            print("Domain allowlist is already up-to-date. No update needed.")
            return

        update_body = mdls.WriteSetting(email_domain_allowlist=combined_domains)
        response = sdk.set_setting(body=update_body)
        print("Email domain allowlist updated successfully:")
        print(response.email_domain_allowlist)

    except SDKError as e:
        print(f"SDK Error while updating email domain allowlist: {str(e)}")
