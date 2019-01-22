#!/bin/bash
DIR="$1"
DIR_TMT_GIT="$2"
LT="$3"
PUBLIC=/public-data/
DEPLOY_DIR=/public-data/web/recursos-dev
PREPROD_DEPLOY_DIR=/public-data/web/recursos-preprod

echo $DIR, $DIR_TMT_GIT
cd $DIR_TMT_GIT && git pull

if [[ -n "${TRANSIFEX_USER}" && -n "${TRANSIFEX_PASSWORD}" ]]; then
    python $DIR_TMT_GIT/docker/credentials/transifex.py
else
    grep -l "type.*transifex" cfg/projects/*.json  | xargs rm -f
fi

if [[ -n "${ZANATA_PROJECT_1}" && -n "${ZANATA_USER_1}"  && -n "${ZANATA_TOKEN_1}" ]]; then
    python $DIR_TMT_GIT/docker/credentials/zanata.py $DIR_TMT_GIT/cfg/credentials/
else
    grep -l "type.*zanata" cfg/projects/*.json  | xargs rm -f
fi

tx --version
cd $LT
java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 7001 &

cd $DIR_TMT_GIT/deployment 
/bin/bash generate-tm.sh $DIR $PUBLIC
if [ -f builder-error.log ]; then cat builder-error.log;fi

/bin/bash generate-terminology.sh $DIR
/bin/bash generate-isolists.sh $DIR

cd $DIR_TMT_GIT/deployment
curl --data "language=en-US&text=a simple test" http://localhost:7001/v2/check
/bin/bash generate-quality.sh $DIR
/bin/bash deploy.sh $DIR $DEPLOY_DIR "" $PUBLIC
/bin/bash # Used for debugging

