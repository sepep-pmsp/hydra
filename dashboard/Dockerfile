FROM python:3.10-slim

# Checkout and install dagster libraries needed to run the gRPC server
# exposing your repository to dagster-webserver and dagster-daemon, and to load the DagsterInstance

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ARG DASH_HOME

# Add repository code
RUN mkdir -p ${DASH_HOME}

# Copy your code  to DASH_HOME
COPY . ${DASH_HOME}

ARG PORT

# expose dash on port
EXPOSE ${PORT}

WORKDIR ${DASH_HOME}

ENTRYPOINT [ "gunicorn" ]

CMD ["app:app"]
