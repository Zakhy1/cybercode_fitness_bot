# pull official base image
FROM python:3.10

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME/static
WORKDIR $APP_HOME

# install python dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# copy project
COPY . $APP_HOME

# create the app user
RUN addgroup --system app && adduser --system --group app && \
    chown -R app:app $APP_HOME


USER app