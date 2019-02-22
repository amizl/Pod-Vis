# CliO

TODO:
1. Introduce api, client and db
2. Talk about filling out environment variables (for flask and db)
3. How to spin up containers
4. How to develop if working on client or API

Quick version.

1. Fill out the fields in /example_env and save this file as .env
2. Fill out the fields in api/example_env and save this file as .env
- There are fields in this file that should map to some fields from /example_env you filled out above. (mysql user, password, etc.)
3. To spin up the containers, in same directory as docker-compose.yml, run `docker-compose build` to build the images. Once built, then run `docker-compose up`.
4. The next step is to find the MySQL container and import our schema and data.
- `docker ps` to find the container id of mysql container
- ``docker exec -i <mysql container id> mysql -uroot --password=<root mysql password set in .env> <database name from env> < db/db_schema_v1.sql`
- Next we want to first make sure our dump.sql file is in the db directory (not committed), then import that file. `docker exec -t -i <mysql container id> mysql -uroot --password=<root mysql password set in .env> <database name from env> < db/dump.sql`
- This container has a volume at db/data/mysql and will persist there.