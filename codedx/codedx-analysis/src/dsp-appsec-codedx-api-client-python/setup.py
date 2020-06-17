from setuptools import setup, find_packages

packages = ["codedx_api"]

setup(
    name='codedx_api',  
    version='0.1',
    author="Sarada Symonds",
    author_email="ssymonds@broadinstitute.org",
    description="CodeDX API Client for Python",
    url="https://github.com/broadinstitute/codedx-api-client",
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: TBD",
        "Operating System :: OS Independent",
    ],
)