---
description: Starting a new project on GCP?
---

# What Compute Environment Should I Use?

## Key Takeaways

* Use pre-built environments like App Engine or Cloud Functions if possible.'
* If you must use GCE, make sure it's' configured securely.

| **Use** | **If your project...** |
| :--- | :--- |
| Cloud Functions (CF) | is written in Node.js, Python, or Go and can be triggered by an "event"(like a Pub/Sub topic or HTTP request). |
| App Engine (GAE) | is a web-based application. |
| Kubernetes Engine (GKE) | has a bunch of different applications that have been Dockerized. |
| Compute Engine (GCE) | has special infrastructure requirements. It is not recommended to use a raw GCE machine unless necessary. |

CF, GAE and GKE all have many security features built-in. GCE has little of that and it is recommended to use the other functions for your base-computing if you can.

## Security of GAE and Cloud Functions

Google manages the infrastructure security of applications run in App Engine and Cloud Functions, which minimizes our risk. Each week, Google applies software and OS updates to these environment, so you don't have to do anything!

