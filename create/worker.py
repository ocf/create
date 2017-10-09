#!/usr/bin/env python3.7
"""Celery worker wrapper.

Reads options from a config file (or command-line arguments), then execs a
celery worker process.
"""
import argparse
import os
import socket
from typing import Tuple


def main():
    """Entrypoint into wrapper."""
    parser = argparse.ArgumentParser(
        description='Process incoming OCF account creation requests.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-l',
        '--log-level',
        default='info',
        help='Logging level',
    )
    parser.add_argument(
        '-c',
        '--config',
        default='/etc/ocf-create/ocf-create.conf',
        help='Config file to read from.',
    )
    parser.add_argument(
        '-d',
        '--debug',
        default=False,
        action='store_true',
        help='Whether to run in debug mode (allows interactive debuggers).',
    )
    args = parser.parse_args()
    extra_args: Tuple[str, ...] = ()

    if args.debug:
        extra_args += ('-P', 'solo')
        os.environ['CREATE_DEBUG'] = '1'

    os.environ['CREATE_CONFIG_FILE'] = args.config

    # We always listen on a queue named after the hostname so that the
    # health check can be sure to hit this host.
    # http://docs.celeryproject.org/en/latest/userguide/routing.html
    queues = [socket.gethostname()]

    # If not in dev mode, add us to the default queue. This allows staff to
    # specify the hostname they're testing on to be sure to hit their instance
    # of create, and also to make sure that real tasks don't hit their
    # instance.
    if not args.debug:
        queues.append('celery')

    os.execvp(
        'celery',
        (
            'celery',
            'worker',
            '-A', 'create.tasks',
            # The default is to spawn one worker per CPU... meaning 32 or 48 workers on Marathon!
            '-c', '4',
            '--without-gossip',
            '--without-mingle',
            '-l', args.log_level,
            '-Q', ','.join(queues),
        ) + extra_args,
    )


if __name__ == '__main__':
    main()
