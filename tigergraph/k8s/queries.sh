#!/bin/bash
set -eu
set -o pipefail

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. vars.sh

python3 -u ../queries.py --para ~/tigergraph/data/parameters-sf${SF}