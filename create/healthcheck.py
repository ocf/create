"""Check the status of this create worker.

This runs the "status" task on a celery queue with the name of this hostname.
http://docs.celeryproject.org/en/latest/userguide/routing.html#manual-routing

If the healthcheck fails, Marathon will bring up additional instances and
retire this one.
"""
import argparse
import configparser
import socket
import ssl
import sys

from celery import Celery
from ocflib.account import submission


def celery_app(conf_file):
    # TODO: reduce duplication with create.tasks
    conf = configparser.ConfigParser()
    conf.read(conf_file)

    celery = Celery(
        broker=conf.get('celery', 'broker').replace('redis://', 'rediss://'),
        backend=conf.get('celery', 'backend').replace('redis://', 'rediss://'),
    )
    celery.conf.broker_use_ssl = {
        'ssl_ca_certs': '/etc/ssl/certs/ca-certificates.crt',
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
    }
    celery.conf.redis_backend_use_ssl = {
        'ssl_ca_certs': '/etc/ssl/certs/ca-certificates.crt',
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
    }

    # TODO: stop using pickle
    celery.conf.task_serializer = 'pickle'
    celery.conf.result_serializer = 'pickle'
    celery.conf.accept_content = {'pickle'}

    return celery


def main():
    parser = argparse.ArgumentParser(
        description='Check the status of this create worker.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-c',
        '--config',
        default='/etc/ocf-create/ocf-create.conf',
        help='Config file to read from.',
    )
    args = parser.parse_args()

    tasks = submission.get_tasks(celery_app(args.config))
    task = tasks.status.apply_async(queue=socket.gethostname(), args=())
    result = task.wait(timeout=5)
    print(result)


if __name__ == '__main__':
    sys.exit(main())
