pushd ../
docker build -t tmt-webapp . -f docker/dockerfile-webapp
popd
docker image ls | grep tmt-webapp



