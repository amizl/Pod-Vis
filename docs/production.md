# Building and deploying to production

# UI
Enter UI directory
`cd /var/www/CliO/ui`.

Install modules if not already installed.
`npm install`.

Build application. This will put our built files in `/var/www/CliO/ui/dist` (js/, css/, img/, & index.html) where our webserver will mount its root.
`npm run build`.

# API
Enter API directory.
`cd /var/www/CliO/api`

Make sure all modules are installed (globally)
`sudo pip3 install -r requirements.txt`

Start (or restart) our Gunicorn process that runs the Flask application
`sudo service supervisor restart`


# Nginx
Restart web server if needed.
`sudo service nginx restart`.
