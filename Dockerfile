FROM python:3.12-alpine

LABEL maintainer="Minituff (James Tufarelli)"

# Copy all these files into /app
COPY requirements.txt headerrc-default.yml app/*.py /app/

# Install dependencies
RUN \
    echo "**** Install ****" && \
    python3 -m pip install --no-cache-dir -r /app/requirements.txt && \
    echo "DEV v2"

# Required for python imports to work
ENV PYTHONPATH=.
ENV PYTHONUNBUFFERED=1 

# When the action runs, it will automatically map the default working directory (GITHUB_WORKSPACE) on the runner with the /github/workspace directory on the container.
# https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action#accessing-files-created-by-a-container-action
VOLUME [ "/github/workspace" ]

# Code file to execute when the docker container starts up
# Args will be passed using CMD
ENTRYPOINT ["python3", "/app/main.py"]

# Do not use: USER or WORKDIR
# https://docs.github.com/en/actions/creating-actions/dockerfile-support-for-github-actions
# --workdir /github/workspace will be used by github