pushd ../
docker build -t tmt-webapp-test . -f docker/dockerfile-webapp-test
popd
docker image ls | grep tmt-webapp-test
