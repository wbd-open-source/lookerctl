import sys
import os
import looker_sdk
from looker_sdk import models40 as mdls
from looker_sdk.error import SDKError

# Ensure imports from parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_content_metadata_id(sdk, folder_id):
    """
    Retrieves the content metadata ID for a given folder.
    """
    try:
        folder = sdk.folder(folder_id)
        return folder.content_metadata_id
    except SDKError as e:
        print(f"Error retrieving content_metadata_id for folder '{folder_id}': {e}")
        return None


def get_group_id_by_name(sdk, group_name):
    """
    Retrieves the group ID for a specified group name.
    """
    try:
        groups = sdk.search_groups(name=group_name)
        if groups:
            return groups[0].id
        else:
            print(f"Group '{group_name}' not found.")
            return None
    except SDKError as e:
        print(f"Error retrieving group ID for '{group_name}': {e}")
        return None


def update_folder_permissions(sdk, group_name, content_metadata_id, access_type="view"):
    """
    Updates folder permissions for a specified group.
    """
    group_id = get_group_id_by_name(sdk, group_name)
    if group_id and content_metadata_id:
        try:
            access_update_payload = mdls.ContentMetaGroupUser(
                group_id=group_id,
                permission_type=access_type.lower(),
                content_metadata_id=content_metadata_id
            )
            sdk.update_content_metadata(content_metadata_id=content_metadata_id, body={'inherits': False})
            sdk.create_content_metadata_access(body=access_update_payload)
            print(f"Permissions updated for group '{group_name}' on content metadata ID {content_metadata_id}.")
        except SDKError as e:
            print(f"Error updating content metadata access: {e}")
    else:
        print(f"Failed to update permissions for '{group_name}' or invalid content metadata ID.")


def create_folders(sdk, parent_folder_id, folder_name):
    """
    Creates a folder in Looker under a specified parent folder.
    """
    try:
        folder_payload = mdls.CreateFolder(name=folder_name, parent_id=parent_folder_id)
        folder = sdk.create_folder(folder_payload)
        print(f"Folder '{folder_name}' created with ID {folder.id}.")
        return folder.id, folder.content_metadata_id
    except SDKError as e:
        print(f"Error creating folder '{folder_name}': {e}")
        return None, None


def get_name_from_access(sdk, access):
    """
    Retrieves the name of a group or user associated with access permissions.
    """
    if access.group_id:
        try:
            group = sdk.group(access.group_id)
            return group.name
        except SDKError as e:
            print(f"Error retrieving group name for group_id '{access.group_id}': {e}")
            return None
    elif access.user_id:
        try:
            user = sdk.user(access.user_id)
            return f"{user.first_name} {user.last_name}"
        except SDKError as e:
            print(f"Error retrieving user name for user_id '{access.user_id}': {e}")
            return None
    return None


def get_content_metadata_access_ids_and_names(sdk, folder_id):
    """
    Retrieves access information for a given folder's content metadata.
    """
    content_metadata_id = get_content_metadata_id(sdk, folder_id)
    if content_metadata_id:
        try:
            access_list = sdk.all_content_metadata_accesses(content_metadata_id=content_metadata_id)
            access_info = []
            for access in access_list:
                name = get_name_from_access(sdk, access)
                access_info.append({
                    "access_id": access.id,
                    "permission_type": access.permission_type,
                    "name": name
                })
            return access_info
        except SDKError as e:
            print(f"Error retrieving content metadata access IDs and types: {e}")
            return []
    else:
        print(f"No content_metadata_id found for folder '{folder_id}'")
        return []


def delete_default_group(sdk, access_data):
    """
    Deletes default group access, specifically for "All Users" group if present.
    """
    try:
        access_id = None
        for data in access_data:
            if data.get('name') == "All Users":
                access_id = data.get('access_id')

        if access_id:
            sdk.delete_content_metadata_access(access_id)
            print(f"Access ID {access_id} for 'All Users' group deleted successfully.")
        else:
            print("No 'All Users' group found or access_id is missing.")

    except KeyError as e:
        print(f"Missing expected key in access data: {e}")
    except AttributeError as e:
        print(f"Invalid structure in access_data (expected iterable of dicts): {e}")
    except SDKError as e:
        print(f"Looker SDK error while deleting access: {e}")
    except TypeError as e:
        print(f"Unexpected data type in access_data: {e}")
    except Exception as e:
        print(f"Unexpected error occurred while deleting content access: {e}")


def create_folders_recursive(sdk, parent_folder_id, folder_structure, yaml_data):
    """
    Recursively creates folders in Looker based on a given folder structure.

    ✨ Updated: Now folder name is used as-is (not prefixed with project name)
    """
    folder_ids = []
    for folder in folder_structure:
        # Folder is created directly with its name under parent
        folder_id, content_metadata_id = create_folders(sdk, parent_folder_id, folder['name'])
        if folder_id and content_metadata_id:
            folder_ids.append(folder_id)

            # Set permissions if defined
            if 'permissions' in folder:
                group_name = folder['permissions'].get('group_name')
                access_type = folder['permissions'].get('access_type', 'view')
                update_folder_permissions(sdk, group_name, content_metadata_id, access_type)

            # Handle subfolders recursively
            if 'subfolders' in folder:
                subfolder_ids = create_folders_recursive(sdk, folder_id, folder['subfolders'], yaml_data)
                folder_ids.extend(subfolder_ids)

            # Clean up default group access
            delete_default_group(sdk, get_content_metadata_access_ids_and_names(sdk, folder_id))
        else:
            print(f"Failed to create folder '{folder['name']}'.")
    return folder_ids


def process_folders(sdk, yaml_data):
    """
    Initiates folder creation from the top level.

    Updated:
    - Creates a root folder using project name under 'Shared'
    - Places all contentFolder folders as subfolders inside it
    """
    shared_folder_id = 'home'
    project_name = yaml_data['project']['name']

    # Create top-level folder for project
    root_folder_id, _ = create_folders(sdk, shared_folder_id, project_name)

    if not root_folder_id:
        print(f" Failed to create root folder '{project_name}' under 'Shared'.")
        return

    # Create all subfolders defined in YAML under root folder
    folder_ids = create_folders_recursive(sdk, root_folder_id, yaml_data['contentFolder'], yaml_data)
    print(f"Created folder IDs: {folder_ids}")
