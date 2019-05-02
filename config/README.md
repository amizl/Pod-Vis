# Configuation Files for Production/Development Server

# nginx.conf
Configuration for web server. This file needs to be symlinked to /etc/nginx/sites-available/cliovis.conf and /etc/nginx/sites-enabled/cliovis.conf.

# supervisor.conf
Configuation for supervisor. This controls and monitors our Flask+gunicorn process. This file needs to be symlinked to /etc/supervisor/conf.d/cliovis.conf
