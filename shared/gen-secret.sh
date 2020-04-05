#!/usr/bin/env bash

set -eu

# Generates GKE secret with variables
# set to passphrases of given lengths

cmd="./kubectl.sh create secret generic $1 -n ${NAMESPACE}" && shift

gen_pass() {
  LC_CTYPE=C tr -dc "a-z0-9" < /dev/urandom | head -c "$1"
}

while (( $# )) ; do
  cmd="${cmd} --from-literal $1=$(gen_pass "$2")"
  shift 2
done

${cmd} || true
