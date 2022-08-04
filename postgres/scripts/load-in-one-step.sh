#!/bin/bash

set -eu
set -o pipefail

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ..

. scripts/vars.sh

if [ ! -d "${POSTGRES_CSV_DIR}" ]; then
    echo "Umbra directory does not exist. \${POSTGRES_CSV_DIR} is set to: ${POSTGRES_CSV_DIR}"
    exit 1
fi

scripts/stop.sh

start_time=$(date +%s.%3N)

scripts/start.sh
scripts/create-db.sh
sleep 5
scripts/load.sh

end_time=$(date +%s.%3N)
elapsed=$(echo "scale=3; $end_time - $start_time" | bc)
echo -e "time\n${elapsed}" > output/load.csv
