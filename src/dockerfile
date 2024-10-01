FROM python:3.12-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install streamlit
RUN pip install streamlit

# Expose the default streamlit port
EXPOSE 8501

# Set the working directory
WORKDIR /app/src/

COPY . /app/src/

#Command to run the Stremlit App
ENTRYPOINT ["streamlit", "run", "app.py"]