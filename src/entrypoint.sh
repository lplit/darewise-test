#!/usr/bin/env bash

exec uvicorn backlog.main:app --host 0.0.0.0 --proxy-headers --forwarded-allow-ips='*' --port 8000 --timeout-keep-alive 20 $@
