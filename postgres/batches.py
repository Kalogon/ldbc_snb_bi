import duckdb
import psycopg2
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time
import pytz
import csv
import re
import sys
import os

print(f"Running DuckDB version {duckdb.__version__}")

print("Datagen / apply batches using SQL")

if len(sys.argv) < 2:
    print("Usage: batches.py <DATA_DIRECTORY>")
    exit(1)

insert_entities = ["Comment", "Comment_hasTag_Tag", "Forum", "Forum_hasMember_Person", "Forum_hasTag_Tag", "Person", "Person_hasInterest_Tag", "Person_knows_Person", "Person_likes_Comment", "Person_likes_Post", "Person_studyAt_University", "Person_workAt_Company", "Post", "Post_hasTag_Tag"]

delete_nodes = ["Comment", "Forum", "Person", "Post"]
delete_edges = ["Forum_hasMember_Person", "Person_knows_Person", "Person_likes_Comment", "Person_likes_Post"]
delete_entities = delete_nodes + delete_edges

data_dir = sys.argv[1]

with open(f"ddl/schema-delete-candidates.sql", "r") as schema_delete_candidates_script_file:
    schema_delete_candidates_script = schema_delete_candidates_script_file.read()

with open(f"dml/snb-deletes.sql", "r") as delete_script_file:
    delete_script = delete_script_file.read()

#con = duckdb.connect(database='ldbc-sql-workflow-test.duckdb')
### PG
pg_con = psycopg2.connect(database="ldbcsnb", host="localhost", user="postgres", password="mysecretpassword",  port=5432)
con = pg_con.cursor()

con.execute(schema_delete_candidates_script)

network_start_date = date(2012, 9, 13)
network_end_date = date(2012, 12, 31)
#network_end_date = date(2012, 9, 15)
batch_size = relativedelta(days=1)

batch_start_date = network_start_date
while batch_start_date < network_end_date:
    # format date to yyyy-mm-dd
    batch_id = batch_start_date.strftime('%Y-%m-%d')
    batch_dir = f"batch_id={batch_id}"
    print(f"#################### {batch_dir} ####################")

    print("## Inserts")
    for entity in insert_entities:
        batch_path = f"{data_dir}/inserts/dynamic/{entity}/{batch_dir}"
        if not os.path.exists(batch_path):
            continue

        print(f"{entity}:")
        for csv_file in [f for f in os.listdir(batch_path) if f.endswith(".csv")]:
            csv_path = f"{batch_path}/{csv_file}"
            print(f"- {csv_path}")
            #con.execute(f"COPY {entity} FROM '{csv_path}' (DELIMITER '|', HEADER, TIMESTAMPFORMAT '%Y-%m-%dT%H:%M:%S.%g+00:00')")
            ### PG
            con.execute(f"COPY {entity} FROM '/data/inserts/dynamic/{entity}/{batch_dir}/{csv_file}' (DELIMITER '|', HEADER, FORMAT csv)")
            pg_con.commit()

    print("## Deletes")
    # Deletes are implemented using a SQL script which use auxiliary tables.
    # Entities to be deleted are first put into {entity}_Delete_candidate tables.
    # These are cleaned up before running the delete script.
    for entity in delete_entities:
        con.execute(f"DELETE FROM {entity}_Delete_candidates")

        batch_path = f"{data_dir}/deletes/dynamic/{entity}/{batch_dir}"
        if not os.path.exists(batch_path):
            continue

        print(f"{entity}:")
        for csv_file in [f for f in os.listdir(batch_path) if f.endswith(".csv")]:
            csv_path = f"{batch_path}/{csv_file}"
            print(f"- {csv_path}")
            #con.execute(f"COPY {entity}_Delete_candidates FROM '{csv_path}' (DELIMITER '|', HEADER, TIMESTAMPFORMAT '%Y-%m-%dT%H:%M:%S.%g+00:00')")
            ### PG
            con.execute(f"COPY {entity}_Delete_candidates FROM '/data/deletes/dynamic/{entity}/{batch_dir}/{csv_file}' (DELIMITER '|', HEADER, FORMAT csv)")
            pg_con.commit()

    print("<running delete script>")
    # Invoke delete script which makes use of the {entity}_Delete_candidates tables
    con.execute(delete_script)
    print("<finished delete script>")

    batch_start_date = batch_start_date + batch_size

con.close()
