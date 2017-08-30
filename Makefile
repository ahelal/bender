MAKEFLAGS += --warn-undefined-variables
.DEFAULT_GOAL := build
PHONY: all build test push push-latest clean

NAME	   := quay.io/ahelal/bender
VERSION    := $(shell cat VERSION)

M = $(shell printf "\033[34;1m▶\033[0m")

all: test squash build

build:
	$(info $(M) Building ${NAME}:${VERSION} and ${NAME}:dev …)
	@docker build -t ${NAME}:${VERSION} -t ${NAME}:dev -f Dockerfile .

squash:
	# requires docker-squash https://github.com/goldmann/docker-squash
	$(info $(M) Squashing ${NAME}:${VERSION} …)
	@docker-squash -t ${NAME}:${VERSION} ${NAME}:${VERSION}

tests:
	$(info $(M) Running tests for )
	@PYTHONPATH="src/lib" nosetests -w "src/tests"

detailed-tests:
	$(info $(M) Running tests for $(VERSION))
	@PYTHONPATH="src/lib" nosetests --detailed-errors -w "src/tests" -vv --nocapture

coverage:
	@coverage report -m src/lib/*.py

lint:
	@pylint src/lib/*.py

push:
	$(info $(M) Pushing $(NAME):$(VERSION) )
	@docker tag $(NAME):dev $(NAME):$(VERSION)
	@docker push "${NAME}:${VERSION}"

push-latest:
	$(info $(M) Linking latest to $(NAME):$(VERSION) and pushing tag latest )
	docker tag $(NAME):$(VERSION) $(NAME):latest
	docker push "${NAME}:latest"

# clean:
# 	$(info $(M) Cleaning)
