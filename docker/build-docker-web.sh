cp dockerfile-webapp dockerfile-webapp-local
sed -i "s+registry.softcatala.org/github/++g" dockerfile-webapp-local
pushd ../
docker build -t tmt-webapp . -f docker/dockerfile-webapp-local
popd
docker image ls | grep tmt-webapp



