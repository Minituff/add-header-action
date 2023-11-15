FROM mcr.microsoft.com/devcontainers/python:3

# Copy necessary files
COPY .devcontainer/scripts /scripts
COPY requirements.txt /requirements.txt

# Run setup commands
RUN \
    bash ./scripts/build.sh

# Entry remains the same from base image