# CircleCI

Safely store secrets using contexts, project environment variables, or third-party solutions such as Vault.

## Security in Circle CI

Circle CI destroys containers and VMs after jobs are finished running.

The default behavior of Circle CI is to never pass secrets to forked pull requests. Running Circle CI processes on forked PR could expose sensitive data, so it should not be enabled.

## Contexts

Contexts are groups of environment variables that can be shared across organizations. Organization administrators (anyone who is an owner of a project in the organization on Github) can restrict contexts to specific groups of people, based on Github teams.

## Project Environment Variables

Anyone with access to the project can add or delete environment variables.

1. In the CircleCI application, go to your project’s settings by clicking the gear icon next to your project.
2. In the Build Settings section, click on Environment Variables.
3. Click the 'Add Variable' button.
4. Enter the value and the key for your variable and click 'Add Variable'.
5. Use your new environment variables in your .circleci/config.yml file.

To change the value of an environment variable, you have to delete it and add it to the project again.

1. In the CircleCI application, go to your project’s settings by clicking the gear icon next to your project.
2. In the Build Settings section, click on Environment Variables.
3. Click the 'X' next to the variable you want to change.
4. Click 'Add Variable' to add the variable again.

## Orbs

CircleCI currently has a registry of "orbs" - pre-built commands and jobs that can be used for processes like signing into to GCP. Using certified orbs from the registry is recommended if possible.

Example:

```text
      version: 2.1
      orbs:
        gcp-cli: circleci/gcp-cli@1.0.0
      workflows:
        install_and_configure_cli:
          # optionally determine executor to use
          executor: default
          jobs:
            - gcp-cli/install_and_initialize_cli:
                context: myContext # store your gCloud service key via Contexts, or project-level environment variables
                google-project-id: myGoogleProjectId
                google-compute-zone: myGoogleComputeZone
```

## Accessing Vault

You can access Vault using Docker or the command line.

```text
  version: 2.1
  jobs:
    build:
      docker: 
        - image: circleci/node:4.8.2 # the primary container, where your job's commands are run
      steps:
        - checkout # check out the code in the project directory
        - run: vault read -format=json secret/path >> config.json
```
