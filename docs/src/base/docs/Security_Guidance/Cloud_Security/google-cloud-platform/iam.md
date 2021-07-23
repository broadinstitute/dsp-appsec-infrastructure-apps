# IAM

### Basic Principles

* Use an approach of "least privilege".
  * Only give users the permissions necessary to perform the tasks they **need** to perform.
  * Avoid giving project-level or owner-level permissions if possible.
* Use separate service accounts for all services. Make sure each service account only has the permissions necessary to do its job.
  * If using Service Accounts, the keys generated should be kept in a VERY safe place, preferably Broad’s “Vault” and rotated at least yearly.
    * https://opensource.google.com/projects/keyrotator
* The IAM Recommender is a feature that tells you if you’ve given people too broad permissions. Log into IAM and see the “light bulb” in your interface. You can click that and right-size people’s permissions.

![](https://lh4.googleusercontent.com/jHdPCTzEcLCL8hGNOcDty6LXjJVyekF1FV-UlH4vG8AprmUkb7JMXFErdNmYVozD8Nkltx8j7BfrBf65bgH3tytA15jyTS14HQv5aqGrkwumHzwWfcgXPritJBexWEElefwOmw7Z)

### 

