DOCKER_REVISION ?= testing-$(USER)
DOCKER_TAG = docker-push.ocf.berkeley.edu/create:$(DOCKER_REVISION)

.PHONY: test
test: autoversion
	pre-commit run --all-files
	pre-commit install -f --install-hooks

.PHONY: builddeb
builddeb: autoversion
	dpkg-buildpackage -us -uc

.PHONY: autoversion
autoversion:
	date +%Y.%m.%d.%H.%M-git`git rev-list -n1 HEAD | cut -b1-8` > .version
	rm -f debian/changelog
	DEBFULLNAME="Open Computing Facility" DEBEMAIL="help@ocf.berkeley.edu" VISUAL=true \
		dch -v `sed s/-/+/g .version` -D stable --no-force-save-on-release \
		--create --package "ocf-create" "Package for Debian."

venv: autoversion vendor/venv-update requirements.txt setup.py
	vendor/venv-update venv= -ppython3.4 venv install= -r requirements.txt -e .

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


.PHONY: clean
clean:
	rm -rf debian/ocf-create debian/*.debhelper create.egg-info debian/*.log debian/ocf-create.substvars

.PHONY: update-requirements
update-requirements:
	$(eval TMP := $(shell mktemp -d))
	virtualenv -p python3 $(TMP)
	. $(TMP)/bin/activate && \
		pip install --upgrade pip && \
		pip install . && \
		pip freeze | grep -v '^create==' | sed 's/^ocflib==.*/ocflib/' > requirements.txt
