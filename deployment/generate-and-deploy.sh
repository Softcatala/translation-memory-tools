#!/bin/bash
# This a sample script that shows how the generate and deploy the application
# You need to modify the paths accordinly to your configuration
# It can be executed as cron task regullary
PATH=$PATH:/usr/local/bin/

ROOT=/home/jmas/dev
DEPLOY_DIR=/home/jmas/web/recursos
PREPROD_DEPLOY_DIR=/home/jmas/web/recursos-preprod

source /home/jmas/web/python-env/bin/activate

# Auto pull changes for dev
cd $ROOT/tm-git
git pull
cd $ROOT

sh $ROOT/tm-git/deployment/generate-tm.sh $ROOT
sh $ROOT/tm-git/deployment/generate-terminology.sh $ROOT
sh $ROOT/tm-git/deployment/generate-lt.sh $ROOT

# Since pology is installed in the system Python
deactivate
sh $ROOT/tm-git/deployment/generate-pology.sh $ROOT
source /home/jmas/web/python-env/bin/activate

sh $ROOT/tm-git/deployment/deploy.sh $ROOT $DEPLOY_DIR $PREPROD_DEPLOY_DIR
