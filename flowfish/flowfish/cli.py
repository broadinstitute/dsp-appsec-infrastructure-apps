"""Console script for flowfish."""
import argparse
import sys


def main():
    """Console script for flowfish."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Fast vulnerability scanner that runs in Google Kubernetes Engine and syncs data into Google Cloud Bigquery "
          "flowfish.cli.main")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
