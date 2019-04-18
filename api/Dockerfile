FROM python:3

WORKDIR /usr/src/app

# Install all our application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code to container
COPY . /usr/src/app

# Run the gunicorn WSGI server and mount it to our flask app,
# port 8080 arbitrarily chosen
CMD gunicorn -b 0.0.0.0:8080 cliovis:app -w 4
