## TODO
Improve this.

## [Wireframes](https://www.lucidchart.com/invitations/accept/d22966aa-8d94-4445-b73d-d7023388035a)

# Pre-reqs

Instructions are for Debian-based systems, but substitute for your platform.

$ sudo apt install mysql-server

# CliO
CliO-Vis is broken up into three parts.
1. API
2. Client
3. DB

## API
The **api** directory is our backend code that serves our python Flask (restful-ish) API. When a request is sent to http://cliovis.io/api or http://cliovis.io/auth, our web server will [reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy) the request to the [GUnicorn](https://gunicorn.org/) WSGI HTTP server that is running our Flask applicaton. Actions such as authenticating a user, or retreiving/processing data from the database is handled here.

## Client
The **ui** directory is our front-end code that serves our SPA. All requests, aside from **/api** and **/auth**, i.e, http://cliovis.io/dashboard, will be handled by our web server / Vue application.

## DB
TODO

# Setting up development
To start, you will need to fill out environment variables for both Docker and Flask.
## Docker
Docker has 3 environment variables it needs when it builds.  Only the root password needs to exist already - the rest will be created automatically.
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_USER`
- `MYSQL_PASSWORD`

These environment variables are loaded when docker builds the MySQL container.
1. See the `example_env` file in the root directory and fill in where it says `TODO`
2. Save this as a new file named: `.env`

## Flask
Flask has 5 environment variables it needs when it initializes,
- `SECRET_KEY` - Secret key for Flask.
- `JWT_SECRET_KEY` - Secret key for JWT. This key is used to sign access tokens for authenticating a user, and subsequently when a user needs to access a protected route (/dashboard).
- `FLASK_CONFIG`- This can be either `development` or `production`. This will enable development/production mode for Flask.
- `MYSQL_DEVELOPMENT_DATABASE_URI` - Database URI to our development DB.
- `MYSQL_PRODUCTION_DATABASE_URI` - Database URI to our production DB. This for now can be the same as development. May change later if we want separate setups.
1. See the `example_env` file in the `api` directory and replace the `TODO` and `<...>` values. The values that start with `<  >` need to be the same as the environment variables you set in the root `.env` file. For example, if this file has
- `MYSQL_USER=cliovis`
- `MYSQL_PASSWORD=cliovis`
- `MYSQL_DATABASE=cliovis`
then the MYSQL_DEVELOPMENT_DATABASE_URI could be
- `MYSQL_DEVELOPMENT_DATABASE_URI=mysql+pymysql://cliovis:cliovis@mysql/cliovis`

The schema will be auto-initialized next, but if there are any custom SQL files (such as a db dump) you want included you should now place them under db/docker-entrypoint-initdb.d/

# Spinning up application
After environment variables are setup, in the root directory (with the docker-compose.yml file),
1. Run `docker-compose build`
2. Run `docker-compose up`
  * You may need to change the ports in the dockerfiles if you already applications running on those ports

# Actively developing api or ui without rebuilding for every change
Building all the containers can impede development if you are only working on a single part of the application. For example, if you are working on the ui, you may want hot reloading so you can see your changes in real time with out having to build all the containers every time.  Do this by:

$ cd api
$ npm install
$ npm run serve

## ui
1. Run `docker-compose build api`
2. Run `docker-compose up api`
This will only build api and its dependencies. Then, to work on the ui, cd in the `ui` directory and
1. Run `npm run serve`
This will launch your ui application on localhost at some port, and it will automatically be communicating with the api docker container. Any changes to ui code will hot reload at this port and doesnt require rebuilding.

## api
TODO (currently required to build and up api because flask + mysql are coupled)


# Quick version.
1. Fill out the fields in /example_env and save this file as .env
2. Fill out the fields in api/example_env and save this file as .env
- There are fields in this file that should map to some fields from /example_env you filled out above. (mysql user, password, etc.)
3. To spin up the containers, in same directory as docker-compose.yml, run `docker-compose build` to build the images. Once built, then run `docker-compose up`.
4. Optional.  The db will automatically be initialized with an empty schema.  Place any other files here: db/docker-entrypoint-initdb.d/
- This container has a volume at db/data/mysql and will persist there.
