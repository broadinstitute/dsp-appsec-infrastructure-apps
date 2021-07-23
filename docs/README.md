# Website

This website is built using [Docusaurus 2](https://docusaurus.io/), a modern static website generator.

## Installation

# TODO

## Local Development

To run locally:


```console
python3 generateFiles.py
docker build --tag external-docs .
docker run -it --rm -d -p 8080:80 --name external external-docs
```

Then go to localhost:8080 in browser.

```console
docker stop external && docker rm external
```

You will need to re-build the docker image each time to see changes made to docs. You only need to run `python3 generateFiles.py` if you add a folder to the `/modules` folder (see below for information).

The `/base` folder includes documentation that should be included with every
deployment of the appsec-apps cluster.

The `/modules` contains documentation for optional features of the appsec-apps cluster
(i.e. CodeDx, etc.). To add a new integration, create a new folder in the `/modules`
folder with an `Overview.md` file, then add the name of that folder to the
`modules` list in the `variables.json` file.

There are some variables you can change in `variables.json`. This will
change some of the text on the site so it can be customized to the Broad Institute.


## Build

# TODO

## Deployment

TODO
