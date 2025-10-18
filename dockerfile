FROM python:3.12-slim

# Set the working directory
WORKDIR /app/src/

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Poetry Install
ENV POETRY_VERSION=2.1.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

# Copy only dependency files first (for caching)
COPY pyproject.toml poetry.lock ./

COPY assets ./assets
COPY src ./src
COPY README.md ./README.md

RUN poetry lock
RUN poetry install

# Expose the default streamlit port
EXPOSE 8501
EXPOSE 8502
EXPOSE 8503

#Command to launch the server
ENTRYPOINT ["poetry", "run", "launchserver"]
