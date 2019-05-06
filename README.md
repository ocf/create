# create

[![Build Status](https://jenkins.ocf.berkeley.edu/buildStatus/icon?job=create/master)](https://jenkins.ocf.berkeley.edu/job/create/job/master/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

Celery worker for account creation

## Development

Clone the repo, and run `make venv` inside the repository directory. This will
install the required python packages needed to run create.

The worker is run in production as a systemd service, but for development you
probably want to just run them manually using the commands explained below. Be
aware that if you start the celery worker but another is already running, you
aren't guaranteed that tasks will land on your instance.

To run the bot, first you must be on supernova, since the credentials are only
accessible from there. Then, after installing the packages required, source the
virtualenv (`source .activate.sh`) to enable the commands to use for running
the celery worker. To automatically source and unsource the virtualenv when
entering/leaving the directory, try using
[aactivator](https://github.com/Yelp/aactivator).

To start the celery worker, run `python -m create.worker --debug`. The celery
worker will by default use the config file already on supernova, but you can
specify your own config file to use for development with the `-c` or `--config`
parameter to either one. More help is available with `-h` or `--help`. To exit
the virtualenv when you are done working on create, just type `deactivate`.

When running with `--debug`, your celery worker will only listen on a queue
named after the hostname it runs on. This means that your worker won't serve
real tasks (e.g. users using prod ocfweb), and that you can always hit your
worker by specifying the right queue (e.g. `supernova`).
