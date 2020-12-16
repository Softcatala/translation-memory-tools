pushd ../
docker build -t tmt-builder . -f docker/dockerfile-builder
popd
docker image ls | grep tmt-builder
