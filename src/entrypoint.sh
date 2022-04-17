#!/usr/bin/env bash

set -e

exec uvicorn backlog.main:app --host 0.0.0.0 --port 8000 $@
