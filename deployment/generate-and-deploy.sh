
# This a sample script that shows how the generate and deploy the application
# You need to modify the paths accordinly to your configuration
# It can be executed as cron task regullary
PATH=$PATH:/usr/local/bin/

ROOT=/home/jmas
DEPLOY_DIR=/var/www/recursos.softcatala.org/dev
PREPROD_DEPLOY_DIR=/var/www/recursos.softcatala.org/preprod

sh $ROOT/tm-git/deployment/generate-tm.sh $ROOT
sh $ROOT/tm-git/deployment/generate-terminology.sh $ROOT
sh $ROOT/tm-git/deployment/deploy.sh $ROOT $TARGET_DIR $PREPROD_DEPLOY_DIR
