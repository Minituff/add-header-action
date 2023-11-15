#!/bin/sh -l

# SUPER SECRET CONFIDENTIAL 
# [2023] - [Infinity and Boyond] ACME CO 
# All Rights Reserved. 
# NOTICE: This is super secret info that 
# must be protected at all costs. 


echo "VAR 1 = $1"

if [ -z "$TEST_DOCKER" ]; then
    time=$(date)
    echo "time=$time" >> $GITHUB_OUTPUT
else
    exec python3 /action/workspace/main.py "--dry-run ${DRY_RUN}"
fi


