#!/bin/bash
#http://172.17.0.2:8080/
cd /srv/web
gunicorn web_search:app -b 0.0.0.0:8080

