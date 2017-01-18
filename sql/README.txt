Scripts supporting the DERP database are stored in this directory. These scripts assume Postgres and may use features incompatible with other database servers. 

To use a script:
psql [database name] < [script name]

where [database name] is the name of the DERP database and [script name] is the filename of the script to execute.

Scripts:
create_tables.sql   - This script creates the tables required by DERP
initial_data.sql    - This script populated the database with initial lookup
                      data (i.e. roles and results)
