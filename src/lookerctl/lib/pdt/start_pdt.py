# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

from looker_sdk import models40
from looker_sdk.error import SDKError

def trigger_pdt_build(sdk, model_name, view_name, workspace='dev', force_rebuild=False, force_full_incremental=False):
    """
    Triggers PDT materialization for the given model and view.

    Parameters:
        sdk: Initialized Looker SDK object
        model_name (str): The model containing the PDT.
        view_name (str): The view representing the PDT.
        workspace (str): 'dev' or 'production'. Default is 'dev'.
        force_rebuild (bool): Force rebuild of dependent PDTs.
        force_full_incremental (bool): Rebuild incremental PDTs from scratch.

    Returns:
        MaterializePDT: Response object from the API
    """
    try:
        response = sdk.start_pdt_build(
            model_name=model_name,
            view_name=view_name,
            workspace=workspace,
            force_rebuild=force_rebuild,
            force_full_incremental=force_full_incremental
        )
        print(f"PDT build triggered for {model_name}.{view_name}")
        return response

    except SDKError as e:
        print(f"SDK Error while triggering PDT build for {model_name}.{view_name}: {e}")
    except (KeyError, ValueError, TypeError) as e:
        print(f"Invalid input parameter for PDT build ({model_name}.{view_name}): {e}")
    except ConnectionError as e:
        print(f"Network issue while connecting to Looker SDK: {e}")
    except TimeoutError as e:
        print(f"PDT build request for {model_name}.{view_name} timed out: {e}")
    except Exception as e:
        print(f"Unexpected error while triggering PDT build for {model_name}.{view_name}: {e}")
