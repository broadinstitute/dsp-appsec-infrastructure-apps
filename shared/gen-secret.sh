#!/usr/bin/env bash

set -euo pipefail

# Generates GKE secret with variables
# set to passphrases of given lengths,
# in a given NAMESPACE.

pass_gen() {
  LC_CTYPE=C tr -dc "a-z0-9" < /dev/urandom | head -c "$1"
}

cmd="kubectl create secret generic $1 -n ${NAMESPACE}" && shift

while (( $# )) ; do
  key=$1 && shift
  pass=$(pass_gen "$1") && shift
  cmd="${cmd} --from-literal ${key}=${pass}"
done

${cmd} || true
