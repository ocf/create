"""Check the number of create workers."""
import argparse
import configparser
import ssl
import sys
import time

from celery import Celery
from ocflib.account import submission


def discover_workers(tasks, n):
    workers = set()
    latencies = []

    for i in range(n):
        start = time.time()

        task = tasks.status.delay()
        result = task.wait(timeout=5)
        workers.add(result['host'])

        latencies.append((time.time() - start) * 1000)

    return workers, latencies


def celery_app():
    # TODO: reduce duplication with create.tasks
    conf = configparser.ConfigParser()
    conf.read('/etc/ocf-create/ocf-create.conf')

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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--num-checks', '-n',
        type=int, default=100,
        help='number of status checks to run',
    )
    args = parser.parse_args(argv)

    tasks = submission.get_tasks(celery_app())
    workers, latencies = discover_workers(tasks, args.num_checks)

    print('{} workers: {}'.format(len(workers), sorted(workers)))
    print('latencies: mean: {:.02f}ms; min: {:.02}ms; max: {:.02f}ms'.format(
        sum(latencies) / len(latencies),
        min(latencies),
        max(latencies),
    ))


if __name__ == '__main__':
    sys.exit(main())
