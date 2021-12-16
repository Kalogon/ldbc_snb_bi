cd "$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" >/dev/null 2>&1 && pwd )"
cd ..

export POSTGRES_VERSION=14.1
export POSTGRES_CONTAINER_NAME=snb-bi-postgres
export POSTGRES_PASSWORD=mysecretpassword
export POSTGRES_DATABASE=ldbcsnb
export POSTGRES_USER=postgres
export POSTGRES_DATA_DIR=`pwd`/scratch/data
export POSTGRES_PORT=5432

if [ ! -v POSTGRES_CSV_FLAGS ]; then
    export POSTGRES_CSV_FLAGS=""
fi
