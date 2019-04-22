# API

Install dependencies:

1. sudo apt install docker.io docker-compose
2. sudo groupadd docker
3. sudo gpasswd -a $USER docker
4. newgrp docker

In the `CliO/` root directory

1. Run `docker-compose build api`
2. then `docker-compose up api`

This will launch the API at `localhost:5000`.

You can either use a REST client such as [Insomnia](https://insomnia.rest/) or [Postman](https://www.getpostman.com/), or curl to make API calls.
