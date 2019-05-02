## Commands

Reread configuration file at /etc/supervisor/conf.d/cliovis.conf
`sudo supervisorctl reread`

Restart supervisor (and hence our Flask+Gunicorn server)
`sudo service supervisor restart`

Check status of Flask app
`sudo supervisorctl status`
