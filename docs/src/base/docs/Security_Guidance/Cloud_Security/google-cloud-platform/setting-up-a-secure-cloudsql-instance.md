---
description: Secure your SQL databases on the cloud....
---

# Setting up a secure CloudSQL instance

## Create a Secure Instance

Create a secure instance and then allow only SSH connections.

![The Public IP option should be checked, but there should not be any authorized networks.](/img/SQL_config.png)

1. When creating a CloudSQL instance, in the **Instance Info** page under **Configuration Options**, check that the database is blocked to the outside world. This is the default option.
2. After creating the instance, click the instance name to open its **Instance details** page.
3. Select the **CONNECTIONS** tab.
4. Scroll down to the **SSL connections** section.
5. Click **Allow only SSL connections**.

##  Set up SQL Proxy

[Cloud SQL Proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy) allows a user with the appropriate permissions to connect to a Cloud SQL database without having to deal with IP whitelisting or SSL certificates manually.

1. You can [install the SQL Proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy#install) locally, or use the [SQL Proxy Docker](https://github.com/GoogleCloudPlatform/cloudsql-proxy#container-images) image supported by Google.
2. Set up Cloud SQL Proxy by following instructions [here](https://cloud.google.com/sql/docs/mysql/sql-proxy#proxy_startup_options).
3. It is recommended to [use a service account for authentication](https://cloud.google.com/sql/docs/mysql/sql-proxy#using-a-service-account).



