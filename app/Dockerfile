FROM python:3.10

# Настройки Poetry
ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache
# Python переменные
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# Установка Poetry
RUN python3 -m venv $POETRY_VENV \
	&& $POETRY_VENV/bin/pip install -U pip setuptools \
	&& $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Добавление Poetry в PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /srv/www/education_platform

# Установка зависимостей
COPY poetry.lock pyproject.toml ./
RUN poetry install

# Запуск приложения
COPY education /srv/www/education_platform
EXPOSE 8000

# Для запуска только контейнера
#CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]