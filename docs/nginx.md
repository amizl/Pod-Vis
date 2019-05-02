# Nginx
Web server that serves our client-side SPA  via `/` and reverse proxies to our Flask server on `/api` and `/auth` endpoints.

## Commands

Stop web server.
`sudo service nginx stop`

Start web server.
`sudo service nginx start`

Restart web server. This needs to be restarted if configuration file changes.
`sudo service nginx restart`
