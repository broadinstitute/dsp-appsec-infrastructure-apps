# Secrets

What to do when a secret is accidentally committed in source code?

## Background

Secrets, such as private keys or API tokens, are regularly leaked by developers in source code repositories. More often than not this happens by accident. Accidents happen, however it's important that the necessary steps are taken as part of mitigation.
Examples of sensitive information:
* API tokens
* Private Keys
* GCP, AWS, Azure Keys
* Passwords, DB Credentials
* Confidential logs, etc.

## How would I know if I accidentally committed a secret?

AppSec teams should be monitoring source code and alert developer teams when a secrets has been leaked.

## Post-Incident Steps to Take

1. First things first, rotate your credentials. Once you have pushed a commit to Github, you should consider any data it contains to be compromised.

2. Remove sensitive info from git history as well: [https://help.github.com/en/articles/removing-sensitive-data-from-a-repository](https://help.github.com/en/articles/removing-sensitive-data-from-a-repository)

3. Review access logs to see if there was some suspicious activity. If you do find suspicious activity please reach out to the application security team.