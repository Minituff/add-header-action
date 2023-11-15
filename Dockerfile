FROM python:3.12-alpine

LABEL maintainer="minituff (James Tufarelli)"

COPY requirements.txt headerrc-default.yml app/*.py /action/workspace/

# Install dependencies
RUN \
    echo "**** Install ****" && \
    python3 -m pip install --no-cache-dir -r /action/workspace/requirements.txt


# When the action runs, it will automatically map the default working directory (GITHUB_WORKSPACE) on the runner with the /github/workspace directory on the container.
# https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action#accessing-files-created-by-a-container-action
VOLUME [ "/github/workspace" ]

# Code file to execute when the docker container starts up
ENTRYPOINT ["python3", "./action/workspace/main.py"]


# Do not use: USER or WORKDIR
# https://docs.github.com/en/actions/creating-actions/dockerfile-support-for-github-actions