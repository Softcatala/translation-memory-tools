# Build builder
bash ./stop-docker.sh
pushd ..
bash ./build-docker-builder.sh  
bash ./build-docker-lt.sh  
popd

# Run builder
mkdir -p tmt-files
docker-compose -f local.yml run -d --use-aliases --name translation-memory-tools-lt tmt-languagetool
docker-compose -f local.yml run -v $PWD$/tmt-files:/srv/tmt-files --use-aliases --name translation-memory-tools tmt-builder
docker cp translation-memory-tools:/srv/web-docker .

docker build -t translation-memory-tools-build-data:master . -f ../dockerfile-data
bash ./stop-docker.sh

# Build web
pushd ..
bash ./build-docker-web.sh
bash ./build-docker-web-test.sh
bash ./run-web-test.sh
popd

