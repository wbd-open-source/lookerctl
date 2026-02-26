import sys
import os
import looker_sdk
from looker_sdk import models40 as mdls

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_folders_starting_with_project_name(sdk, project_name):
    """
    Retrieves folders in Looker that start with the specified project name.

    Parameters:
        project_name (str): The project name used as the prefix for folder names.

    Process:
        - Fetches all folders using the Looker SDK.
        - Filters folders to include only those that start with the specified project name.
        - Prints the names of matching folders or a message if none are found.

    Returns:
        list: A list of folder objects whose names start with the specified project name.
    """
    try:
        folders = sdk.all_folders()
        folders_starting_with_project = [
            folder for folder in folders if folder.name.startswith(project_name)
        ]
        if folders_starting_with_project:
            print(f"Folders starting with '{project_name}': {[folder.name for folder in folders_starting_with_project]}")
        else:
            print(f"No folders found starting with '{project_name}'")
        return folders_starting_with_project
    except looker_sdk.error.SDKError as e:
        print(f"Error fetching folders: {e}")
        return []


def delete_folder(sdk, folder_id):
    """
    Deletes a folder in Looker by its ID.

    Parameters:
        folder_id (str): The ID of the folder to delete.

    Process:
        - Calls the Looker SDK to delete the specified folder.
        - Prints a success message if deletion is successful or an error if deletion fails.
    """
    try:
        sdk.delete_folder(folder_id)
        print(f"Folder with ID '{folder_id}' deleted successfully!")
    except looker_sdk.error.SDKError as e:
        print(f"Error deleting folder with ID '{folder_id}': {e}")


def get_prefixed_folders(sdk, yaml_data, project_name):
    """
    Generates a list of folder names from the YAML configuration, prefixed with the project name.

    Parameters:
        yaml_data (dict): YAML configuration data containing folder structure.
        project_name (str): The project name to use as a prefix for folder names.

    Process:
        - Recursively traverses the folder structure in the YAML data.
        - Appends each folder's full name (prefixed with the project name) to the result list.

    Returns:
        list: A list of prefixed folder names from the YAML configuration.
    """
    prefixed_folders = []

    def traverse_folders(folders, parent_id=''):
        for folder in folders:
            full_folder_name = f"{project_name}_{folder['name']}"
            prefixed_folders.append(full_folder_name)
            if 'subfolders' in folder:
                traverse_folders(folder['subfolders'], full_folder_name)
    content_folders = yaml_data.get('contentFolder', [])
    if content_folders:
        traverse_folders(content_folders)

    return prefixed_folders


def delete_unused_folders(sdk, yaml_data):
    """
    Deletes folders in Looker that are not listed in the YAML configuration.

    Parameters:
        yaml_data (dict): YAML configuration data containing project and folder details.

    Process:
        - Retrieves folders from Looker that start with the project name.
        - Compares Looker folder names to those defined in YAML, identifying unused folders.
        - Deletes each unused folder and any associated subfolders.

    Usage:
        This function is typically run at startup to clean up folders not specified in the YAML configuration.
    """
    if yaml_data['project']['name']:
        project_name = yaml_data['project']['name']
    else:
        print("Project Name is not available in Yaml.")
    looker_folders = get_folders_starting_with_project_name(sdk, project_name)
    yaml_folder_names = get_prefixed_folders(sdk, yaml_data, project_name)

    if not isinstance(yaml_folder_names, list):
        print("Error: 'folders' in YAML is not a list")
        return

    folder_names = [folder.name for folder in looker_folders]
    print(folder_names)
    print(yaml_folder_names)
    folders_to_delete = [folder for folder in looker_folders if folder.name not in yaml_folder_names]

    print('Folders to delete:', [folder.name for folder in folders_to_delete])

    for folder in folders_to_delete:
        print(f"Folder '{folder.name}' does not exist in YAML. Deleting...")

        subfolders = sdk.folder_children(folder.id)
        for subfolder in subfolders:
            print(f"Subfolder '{subfolder.name}' deleted.")
            delete_folder(sdk, subfolder.id)

        delete_folder(sdk, folder.id)
