.PHONY: docker-build-builder docker-build-lt docker-build-webapp docker-run-builder docker-run-webapp docker-run-webapp-test docker-build-gitlab-data-debug docker-run-gitlab-data-debug

docker-build-builder:
	docker build -t tmt-builder . -f docker/dockerfile-builder;

docker-build-lt:
	cd docker && docker build -t tmt-languagetool . -f dockerfile-languagetool;

docker-build-webapp:
	docker build --no-cache -t tmt-webapp . -f docker/dockerfile-webapp;

docker-build-webapp-test: docker-build-webapp
	docker build --no-cache -t tmt-webapp-test . -f docker/dockerfile-webapp-test;

docker-build-gitlab-data-debug:
	docker build --no-cache -t tmt-dockerfile-gitlab-data-debug . -f docker/dockerfile-gitlab-data-debug;

docker-run-gitlab-data-debug: docker-build-gitlab-data-debug
	docker run -i -t tmt-dockerfile-gitlab-data-debug;

docker-run-builder: docker-build-builder docker-build-lt
	./docker/stop-docker.sh
	docker-compose -f docker/local.yml run -d --use-aliases --name translation-memory-tools-lt tmt-languagetool;
	docker-compose -f docker/local.yml run -v $PWD$/tmt-files:/srv/tmt-files --use-aliases --name translation-memory-tools tmt-builder;
	docker cp translation-memory-tools:/srv/web-docker .;
	docker build -t tmt-data . -f docker/dockerfile-data;
	./docker/stop-docker.sh;

docker-run-webapp: docker-build-webapp
	docker run -p 8080:8080 -i -t tmt-webapp;

docker-run-webapp-test: docker-build-webapp-test
	docker run -p 8080:8080 -i -t tmt-webapp-test;
