# Website

This folder contains files for 

1. Building an image containing external, public-facing documentation.
2. Building and deploying the public-facing documentation.
3. Deploying organization-facing (internal) documentation (the source code is kept in a separate repo and creates an image that is stored in Google Container Registry).

The documentation images are built using Docusaurus.

## Local Development for External Documentation

To run locally:


```console
python3 generateFiles.py
docker build --tag external-docs .
docker run -it --rm -d -p 8080:80 --name external external-docs
```

Then go to localhost:8080 in browser.

```console
docker stop external
```

You will need to re-build the docker image each time to see changes made to docs. You only need to run `python3 generateFiles.py` if you add a folder to the `/modules` folder (see below for information) or if you make changes to `Dockerfile.template` and `src/base/docusaurus.config.js.template` files - please make changes here and not the `Dockerfile` and `src/base/docusaurus.config.js` files.

The `/base` folder includes documentation that should be included with every
deployment of the appsec-apps cluster.

The `/modules` folder contains documentation for services of the appsec-apps cluster
(i.e. CodeDx, SDARQ, etc.). This makes each service "optional" within the documentation site. To add a new integration, create a new folder in the `/modules`
folder with an `Overview.md` file, then add the name of that folder to the
`modules` list in the `variables.json` file.

There are some variables you can change in `variables.json`. This will
change some of the text on the site so it can be customized to the Broad Institute (or to other organizations after open sourcing).


## Build

The external documentation is built by the `dsp-appsec-iinfrastructure-apps/cloudbuild.yaml` file using `EXT_DOCS_IMAGES` environment variable.

## Deployment

External documentation is deployed using `cloudbuild.yaml` and the `deploy.sh`, `deployment.yaml`, and `ingress.yaml`. Internal documentation is deployed using `cloudbuild.yaml` and the `internal.sh`, `internal.yaml`, and `ingress.yaml`.