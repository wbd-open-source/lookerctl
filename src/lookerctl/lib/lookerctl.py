# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import sys
import os
import click
import yaml

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import folders.delete_folder # noqa: E402
import user_attribute.create_user_attributes # noqa: E402
import model.check # noqa: E402
import model.delete_model_set # noqa: E402
import permission.delete_permission_set # noqa: E402
import project.create_project # noqa: E402
import project.github_integration # noqa: E402
import connections.db_connections # noqa: E402
import model.models # noqa: E402
import model.model_set # noqa: E402
import role.create_role # noqa: E402
import folders.final_create # noqa: E402
import permission.create_permission_set # noqa: E402
import role.delete_role # noqa: E402
import saml.create_saml # noqa: E402
import saml.group # noqa: E402
import domain_allowlist.update_email_domain_allowlist # noqa: E402
from pdt import start_pdt  #   noqa: E402
import datagroup.update_datagroup # noqa: E402
from looker_utils import get_sdk # noqa: E402


def get_yaml_sdk(env, config_folder):
    """
    Initializes the SDK and loads merged YAML config (common + env-specific).

    Parameters:
        env (str): Environment to deploy the project (e.g., 'dev' or 'prod').
        config_folder (str): Path to the folder containing YAML config files.

    Returns:
        tuple: (sdk, merged_yaml_data or None)
    """
    yaml_data = None
    env_file = f"{env.lower()}.yaml"


    required_files = {"common.yaml", env_file}
    present_files = set(os.listdir(config_folder))
    missing_files = required_files - present_files

    if missing_files:
        print(f" Missing required YAML file(s): {', '.join(missing_files)} in folder '{config_folder}'")

        return get_sdk(env), None

    try:
        with open(os.path.join(config_folder, "common.yaml"), 'r') as f:
            common_data = yaml.safe_load(f) or {}

        with open(os.path.join(config_folder, env_file), 'r') as f:
            env_data = yaml.safe_load(f) or {}

        yaml_data = {**common_data, **env_data}

    except FileNotFoundError as e:
        print(f"YAML file not found: {e.filename}")
        yaml_data = None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        yaml_data = None
    except OSError as e:
        print(f"I/O error occurred: {e}")
        yaml_data = None

    sdk = get_sdk(env)
    return sdk, yaml_data


@click.group()
def cli():
    """A CLI tool for managing Looker resources using YAML configurations."""
    click.echo("Use --help to see available commands.")


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_project(env, config):
    """
    Creates a Looker project based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Creating project with config in {env} environment.")
    project.create_project.create_project(sdk, yaml_data, env)



@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_git_integration(env, config):
    """
    Creates a Looker github integration based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Creating github integration with config in {env} environment.")
    project.github_integration.configure_git_for_project(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_model(env, config):
    """
    Creates a model in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Creating model with config in {env} environment.")
    model.models.create_models_from_yaml(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def delete_model(env, config):
    """
    Deletes unused models in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Deleting model with config in {env} environment.")
    model.check.delete_unused_models(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_role(env, config):
    """
    Manages and creates roles in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Managing roles with config in {env} environment.")
    role.create_role.process_roles(sdk, env, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def delete_role(env, config):
    """
    Deletes unused roles in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Deleting unused roles with config in {env} environment.")
    role.delete_role.delete_unused_roles(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_model_set(env, config):
    """
    Creates model sets in Looker based on YAML configuration.
    """
    click.echo(f"Creating model set with config in {env} environment.")
    sdk, yaml_data = get_yaml_sdk(env, config)
    model.model_set.process_model_sets(sdk, yaml_data)
    model.model_set.create_default_model_set(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def delete_model_set(env, config):
    """
    Deletes model sets in Looker based on YAML configuration.
    """
    click.echo(f"Deleting model set with config in {env} environment.")
    sdk, yaml_data = get_yaml_sdk(env, config)
    model.delete_model_set.delete_unused_model_sets(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_folder(env, config):
    """
    Creates folders in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Creating folders with config in {env} environment.")
    folders.final_create.process_folders(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def delete_folder(env, config):
    """
    Deletes folders in Looker based on YAML configuration.
    """
    click.echo(f"Deleting folders with config in {env} environment.")
    sdk, yaml_data = get_yaml_sdk(env, config)
    folders.delete_folder.delete_unused_folders(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_permissions(env, config):
    """
    Creates permission sets in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Creating permissions with config in {env} environment.")
    permission.create_permission_set.process_permission_sets(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def delete_permissions(env, config):
    """
    Deletes permission sets in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Deleting permissions with config in {env} environment.")
    permission.delete_permission_set.delete_unused_permission_sets(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_db_connection(env, config):
    """
    Creates database connections in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Creating database connection with config in {env} environment.")
    connections.db_connections.create_connection_based_on_dialect('us-east-1', sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def delete_db_connection(env, config):
    """
    Deletes database connections in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Deleting database connection with config in {env} environment.")
    connections.delete_db_connection.delete_unused_connections(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_user_attributes(env, config):
    """
    Creates user attributes in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Creating User Attributes with config in {env} environment.")
    user_attribute.create_user_attributes.process_user_attributes(sdk, yaml_data)

@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def update_saml(env, config):
    """
    Updates the SAML in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    yaml_data = yaml_data.get('saml', [])
    click.echo(f"updating the SAML with config in {env} environment.")
    saml.create_saml.update_saml_groups_from_yaml(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def update_domain_allowlist(env, config):
    """
    Updates the email domain allowlist in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    click.echo(f"Updating the Domain Allow List with config in {env} environment.")
    domain_allowlist.update_email_domain_allowlist.update_domain_allowlist(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_group(env, config):
    """
    Creates the Group in Looker based on YAML configuration.
    """
    sdk, yaml_data = get_yaml_sdk(env, config)
    groups = yaml_data.get('groups', [])
    click.echo(f"Creating Looker groups with config in {env} environment.")
    saml.group.create_groups_from_yaml(sdk, groups)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--config', default='config.yaml', help='YAML configuration file path')
def create_all(env, config):
    """
    A comprehensive creation command that processes all Looker components based on YAML configuration.
    """

    sdk, yaml_data = get_yaml_sdk(env, config)
    if 'project' in yaml_data:
        project.create_project.create_project(sdk, yaml_data, env)
    if 'model' in yaml_data:
        model.models.create_models_from_yaml(sdk, yaml_data)
    if 'access_control' in yaml_data:
        if 'permission_sets' in yaml_data['access_control']:
            permission.create_permission_set.process_permission_sets(sdk, yaml_data)
        if 'model_set' in yaml_data['access_control']:
            model.model_set.process_model_sets(sdk, yaml_data)
            model.model_set.create_default_model_set(sdk, yaml_data)
        if 'roles' in yaml_data['access_control']:
            role.create_role.process_roles(sdk, env, yaml_data)
        if 'user_attributes' in yaml_data['access_control']:
            user_attribute.create_user_attributes.process_user_attributes(sdk, yaml_data)
    if 'connections' in yaml_data:
        connections.db_connections.create_connection_based_on_dialect('us-east-1', sdk, yaml_data)
    if 'contentFolder' in yaml_data:
        folders.final_create.process_folders(sdk, yaml_data)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--model_name', help='Model name of the PDT')
@click.option('--view_name', help='Name of the PDT')
@click.option('--workspace', help='Dev or production. Default is Production')
@click.option('--force_rebuild', help='(bool): Force rebuild of dependent PDTs')
@click.option('--force_full_incremental', help='(bool): Rebuild incremental PDTs from scratch.')
def pdt_trigger(env, model_name, view_name, workspace, force_rebuild, force_full_incremental):
    """
    Triggers the PDT 
    """
    sdk = get_sdk(env)
    click.echo(f"Triggering the PDT {view_name} in {env} environment.")
    start_pdt.trigger_pdt_build(sdk, model_name, view_name, workspace, force_rebuild, force_full_incremental)


@click.command()
@click.option('--env', default='dev', help='Specify the environment (e.g., dev, QA).')
@click.option('--datagroupname', default='config.yaml', help='YAML configuration file path')
@click.option('--modelname', default='config.yaml', help='YAML configuration file path')
def trigger_datagroup(env, datagroupname, modelname):
    """
    Triggers the DataGroup with config 
    """
    click.echo(f"Triggering the DataGroup with config in {env} environment.")
    sdk = get_sdk(env)
    datagroup.update_datagroup.trigger_datagroup(sdk, datagroupname, modelname)


cli.add_command(create_all)
cli.add_command(create_project)
cli.add_command(create_model)
cli.add_command(delete_model)
cli.add_command(create_role)
cli.add_command(delete_role)
cli.add_command(create_permissions)
cli.add_command(delete_permissions)
cli.add_command(create_model_set)
cli.add_command(delete_model_set)
cli.add_command(create_folder)
cli.add_command(delete_folder)
cli.add_command(create_db_connection)
cli.add_command(delete_db_connection)
cli.add_command(create_user_attributes)
cli.add_command(create_git_integration)
cli.add_command(pdt_trigger)
cli.add_command(trigger_datagroup)
cli.add_command(update_saml)
cli.add_command(update_domain_allowlist)
cli.add_command(create_group)


if __name__ == '__main__':
    cli()
