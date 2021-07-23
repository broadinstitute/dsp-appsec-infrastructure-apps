# Github Actions

Generally, we prefer using internal workflows for Github Actions. If you want to use an action on the Github Marketplace, make sure to verify the action is safe and then pin the action's version to your workflow using the commit hash. If you are not sure whether a third-party action is secure, please consult the Application Security team.

### 1. Go to the third party Action's repo.

![Greeting Action on Github Marketplace](/img/hello-action.png)

### 2. Verify that the source code is secure, and find the commit hash for that version.

![Commit hash for Hello Action](/img/hello-commit-sha.png)

### 3. Use the commit hash to specify the third party action's version in your workflow.

![Specify the third party Action&apos;s commit hash in your workflow.](/img/hello-workflow.png)