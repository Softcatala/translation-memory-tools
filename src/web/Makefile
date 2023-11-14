.PHONY: docker-build-webapp docker-run-builder docker-run-webapp docker-run-webapp-test

docker-build-webapp:
	docker build --no-cache -t tmt-webapp . -f docker/dockerfile-webapp;

docker-build-webapp-test: docker-build-webapp
	docker build --no-cache -t tmt-webapp-test . -f docker/dockerfile-webapp-test;

docker-run-webapp: docker-build-webapp
	docker run -p 8080:8080 -i -t tmt-webapp;

docker-run-webapp-test: docker-build-webapp-test
	docker run -p 8080:8080 -i -t tmt-webapp-test;
