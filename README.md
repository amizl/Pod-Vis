## TODO
Improve this.

# CliO
CliO-Vis is broken up into three parts.
1. API
2. Client
3. DB

## API
The **api** directory is our backend code that serves our python Flask (restful-ish) API. When a request is sent to http://cliovis.io/api or http://cliovis.io/auth, our web server will [reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy) the request to the [GUnicorn](https://gunicorn.org/) WSGI HTTP server that is running our Flask applicaton. Actions such as authenticating a user, or retreiving/processing data from the database is handled here.

## Client
The **client** directory is our front-end code that serves our SPA. All requests, aside from **/api** and **/auth**, i.e, http://cliovis.io/dashboard, will be handled by our web server / Vue application.

## DB
TODO

# Setting up development
To start, you will need to fill out environment variables for both Docker and Flask.
## Docker
Docker has 4 environment variables it needs when it builds: `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`. These environment variables are loaded when docker builds the MySQL container.
1. See the `example_env` file in the root directory and fill in where it says `TODO`
2. Save this as a new file named: `.env`

## Flask
Flask has 5 environment variables it needs when it initializes,
- `SECRET_KEY` - Secret key for Flask.
- `JWT_SECRET_KEY` - Secret key for JWT. This key is used to sign access tokens for authenticating a user, and subsequently when a user needs to access a protected route (/dashboard).
- `FLASK_CONFIG`- This can be either `development` or `production`. This will enable development/production mode for Flask.
- `MYSQL_DEVELOPMENT_DATABASE_URI` - Database URI to our development DB.
- `MYSQL_PRODUCTION_DATABASE_URI` - Database URI to our production DB. This for now can be the same as development. May change later if we want separate setups.
1. See the `example_env` file in the `api` directory and replace the `TODO` and `<...>` values. The values that start with `<  >` need to be the same as the environment variables you set in the root `.env` file. For example, if this file has `MYSQL_USER=cliovis`, `MYSQL_PASSWORD`, `MYSQL_DATABASE=cliovis` then a URI could be `mysql+pymysql://cliovis:cliovis@mysql/cliovis`

# Spinning up application
After environment variables are setup, in the root directory (with the docker-compose.yml file),
1. Run `docker-compose build`
2. Run `docker-compose up`
..* You may need to change the ports in the dockerfiles if you already applications running on those ports

# How to work on client container without rebuilding for every change
Building all the containers can impede development if you are only working on a single part of the application. For example, if you are working on the client, you may want hot reloading so you can see your changes in real time with out having to build the containers every time.
1. Run `docker-compose build api`
2. Run `docker-compose up api`
This will only build the containers that are in the api docker name and its dependencies. Then, to work on the client, cd in the `client` directory and
1. Run `npm run serve`
This will launch your client application on locahost at some port, and it will automatically be communicating with the api docker container. Any changes to client code will hot reload at this port and doesnt require rebuilding.


# Quick version.
1. Fill out the fields in /example_env and save this file as .env
2. Fill out the fields in api/example_env and save this file as .env
- There are fields in this file that should map to some fields from /example_env you filled out above. (mysql user, password, etc.)
3. To spin up the containers, in same directory as docker-compose.yml, run `docker-compose build` to build the images. Once built, then run `docker-compose up`.
4. The next step is to find the MySQL container and import our schema and data.
- `docker ps` to find the container id of mysql container
- ``docker exec -i <mysql container id> mysql -uroot --password=<root mysql password set in .env> <database name from env> < db/db_schema_v1.sql`
- Next we want to first make sure our dump.sql file is in the db directory (not committed), then import that file. `docker exec -t -i <mysql container id> mysql -uroot --password=<root mysql password set in .env> <database name from env> < db/dump.sql`
- This container has a volume at db/data/mysql and will persist there.
