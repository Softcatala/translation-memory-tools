#!/bin/bash
cd $LT
java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 7001 --public
