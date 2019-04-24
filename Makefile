DOCKER_REVISION ?= testing-$(USER)
DOCKER_TAG = docker-push.ocf.berkeley.edu/create:$(DOCKER_REVISION)

.PHONY: test
test: venv
	venv/bin/pre-commit run --all-files
	venv/bin/pre-commit install -f --install-hooks

venv: vendor/venv-update requirements.txt requirements-dev.txt
	vendor/venv-update venv= -ppython3.7 venv install= -r requirements.txt -r requirements-dev.txt

.PHONY: cook-image
cook-image:
	# TODO: make ocflib version an argument
	docker build --pull -t $(DOCKER_TAG) .

.PHONY: push-image
push-image:
	docker push $(DOCKER_TAG)

.PHONY: dev
dev: cook-image
	docker run --rm \
		-v /etc/ocf-create-new:/etc/ocf-create:ro \
		$(DOCKER_TAG)

.PHONY: update-requirements
update-requirements: venv
	venv/bin/upgrade-requirements
	sed -i 's/^ocflib==.*/ocflib/' requirements.txt
