# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import looker_sdk
from looker_sdk import models40 as mdls
from looker_sdk.error import SDKError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def update_saml_groups_from_yaml(sdk, saml_groups):
    try:
        all_looker_groups = sdk.all_groups()
        all_roles = sdk.all_roles()
        saml_config = sdk.saml_config()
        existing_groups = saml_config.groups_with_role_ids or []

        def get_group_id(name):
            match = next((g for g in all_looker_groups if g.name == name), None)
            if not match:
                raise ValueError(f"Looker group '{name}' not found")
            return match.id

        def get_role_ids(names):
            ids = []
            for name in names:
                match = next((r for r in all_roles if r.name == name), None)
                if not match:
                    raise ValueError(f"Role '{name}' not found")
                ids.append(str(match.id))
            return ids

        existing_by_name = {g.name: g for g in existing_groups}
        updated_groups = []

        for group in saml_groups:
            looker_group_name = group["looker_group_name"]
            saml_name = group["name"]
            role_names = group["role_names"]
            role_ids = get_role_ids(role_names)
            existing = existing_by_name.get(saml_name)
            updated_groups.append({
                "id": existing.id if existing else None,
                "looker_group_name": looker_group_name,
                "name": saml_name,
                "role_ids": role_ids,
                "url": existing.url if existing else None
            })

        updated_group_names = set(g["name"] for g in updated_groups)
        final_payload = updated_groups + [
            {
                "id": g.id,
                "looker_group_name": g.looker_group_name,
                "name": g.name,
                "role_ids": g.role_ids,
                "url": g.url
            }
            for g in existing_groups
            if g.name not in updated_group_names
        ]

        test_payload = mdls.WriteSamlConfig(groups_with_role_ids=final_payload)

        try:
            test_result = sdk.create_saml_test_config(body=test_payload)
            if test_result and test_result.groups_with_role_ids and len(test_result.groups_with_role_ids) == len(final_payload):
                print("SAML test config validated successfully.")
                sdk.update_saml_config(body=test_payload)
                print("SAML group-role mappings updated successfully.")
            else:
                print("SAML test config validation failed. Mappings mismatch or empty response.")
                raise RuntimeError("SAML update aborted due to failed test config validation.")
        except SDKError as e:
            print(f"SAML test config or update failed: {e}")
            raise
    except Exception as e:
        print(f"Error in processing SAML group-role mappings: {e}")
        raise
