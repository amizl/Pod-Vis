# Entry point for our WSGI server (gunicorn) to run the flask application

import os
from app import create_app

# FLASK_CONFIG should be set inside our .env file. This will either be
# production, development, or testing
config_name = os.environ.get('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == "__main__":
    app.run()
