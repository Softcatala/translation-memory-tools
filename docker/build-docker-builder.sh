pushd ../
docker build -t tmt-builder . -f docker/dockerfile-builder --no-cache
popd
docker image ls | grep tmt-builder
