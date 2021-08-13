#!/bin/bash
cd /srv/web
gunicorn web_search:app -b 0.0.0.0:8080 &
sleep 20s
cd /srv/integration-tests
python run.py -e localhost

