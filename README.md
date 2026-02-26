<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- PROJECT SHIELDS -->

<!-- PROJECT LOGO -->
<br />

<h3 align="center">Lookerctl - Looker IaC Framework</h3>

</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#About-the-project">About The Project</a>
    </li>
    <li>
      <a href="#Introduction">Getting Started</a>
    </li>
    <li><a href="#Prerequisites">Prerequisites</a></li>
    <li><a href="#Step-by-Step-Local-Setup">Local setup</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#Examples">Examples</a></li>
    <li><a href="#Testing">Testing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About-the-project
# Lookerctl - Looker IaC Framework


## Introduction
This project is an automation framework designed to simplify and streamline the process of managing Looker projects through the Looker API. The framework provides functions to automate tasks such as creating projects, assigning user roles, and configuring models based on structured input files (YAML). It ensures consistent and error-free project setup by validating input configurations and handling errors gracefully. 

Key Features:
- Automates Looker project creation based on configuration files.
- Simplifies user role assignments and access management.
- Validates YAML configuration files before execution.
- Comprehensive error handling and logging.
- Unit tests for validation, API errors, and success scenarios.

## Prerequisites
- **Python 3.x**: Make sure Python is installed on your system.
- **Looker API Credentials**: You will need to generate API credentials from your Looker instance.

## Step-by-Step-Local-Setup

- **Clone the repository:**

     git clone oss@example.com:<github-owner>/lookerctl.git

- **Change Directory**

      cd lookerctl

    

  ## Run steps to setup the environment:

  After cloning the repository, you can automate the setup process by running the `setup_env.sh` script. This will create a Python virtual environment, install the dependencies, and set up the project.

  Run the below commands:

  **Create a Python virtual environment:**

        python3 -m venv looker_venv


  **Activate the virtual environment:**

        source looker_venv/bin/activate


  **Install dependencies:**

        pip install -r requirements.txt


  **Run the setup script:**

        python setup.py   


  3. Export the Looker Credentials as environment varibales

    To setup the environment variables, follow this commands:

      
        * export LOOKER_ENV_LOOKER_HOSTNAME= "your hostname"

        * export LOOKER_ENV_CLIENT_ID= "your Client ID"

        * export LOOKER_ENV_CLIENT_SECRET= "your looker secret"


  4. You're now ready to use the framework.

## Usage
Once you have the framework set up, you can use the following functions to automate various Looker tasks:

### 1. **List all the commands that can executed using lookerctl cli**
Use the below command to list all the commands of lookerctl

Command:

    lookerctl --help

### 2. **Create a Looker Project**
Use the framework to create a new Looker project by defining it in the configuration file.

Command:

    lookerctl create-project --config config.yaml
  
  This will read the YAML configuration file, create the Looker project, and assign roles based on the defined users and permissions.

### 3. **Assign User Roles**
Use the framework to create a new Looker roles by defining it in the configuration file.

Command:
    
    lookerctl create-role --config config.yaml --env 
  
## Examples

Here are the some examples commands, how to execute the lookerctl
- lookerctl create-project --config="file_path" --env="dev or prod"
- lookerctl create-model --config="file_path" --env="dev or prod"
- lookerctl create-model-set --config="file_path" --env="dev or prod"
- lookerctl create-role --config="file_path" --env="dev or prod"
- lookerctl create-permission-set --config="file_path" --env="dev or prod"
- lookerctl create-user-attributes --config="file_path" --env="dev or prod"
- lookerctl create-connection --config="file_path" --env="dev or prod"
- lookerctl create-folder --config="file_path" --env="dev or prod"

## Testing
The framework includes unit tests that cover various aspects, including successful project creation, validation errors, and API failures. Before deploying or integrating it into your workflow, you can run the tests to ensure everything works as expected.

### Running Unit Tests:
To execute the tests:

    pytest tests/


Tests include:
- **YAML Validation**: Ensures the configuration file is correctly formatted and contains all necessary fields.
- **API Response Validation**: Verifies the API calls return the expected responses.
- **Error Handling**: Simulates API failures or incorrect configurations to test the framework's error handling capabilities.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
