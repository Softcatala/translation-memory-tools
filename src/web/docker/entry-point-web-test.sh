#!/bin/bash
cd /srv/web
gunicorn web_search:app -b 0.0.0.0:8080 &
while ! httping -qc1 http://localhost:8080 ; do sleep 1 ; echo "Waiting for server to respond"; done
cd /srv/integration-tests
python run.py -e localhost

