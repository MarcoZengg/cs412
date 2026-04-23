#!/usr/bin/env bash
set -e

# Export vars from your secure env file
set -a
source /home/ugrad/xiankz23/secrets/geoguesser/.env
set +a

cd /home/ugrad/xiankz23/webapps/django/project
