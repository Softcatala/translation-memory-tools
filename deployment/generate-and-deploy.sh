PATH=$PATH:/usr/local/bin/

ROOT=/home/jmas
TARGET_DIR=/var/www/recursos.softcatala.org

sh $ROOT/tm-git/deployment/generate-tm.sh $ROOT 
sh $ROOT/tm-git/deployment/generate-terminology.sh $ROOT
sh $ROOT/tm-git/deployment/deploy.sh $ROOT $TARGET_DIR
