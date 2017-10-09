"""Celery worker entrypoint.

This module is not intended to be imported directly, but instead to be used as
the `-A` argument to the celery worker.

The create-worker script will handle reading settings from files, setting
appropriate environment variables, and exec-ing celery. It is the recommended
way to use create.
"""
import os
import ssl
from configparser import ConfigParser
from textwrap import dedent
from traceback import format_exc

from celery import Celery
from celery.signals import setup_logging
from ocflib.account.submission import AccountCreationCredentials
from ocflib.account.submission import get_tasks
from ocflib.misc.mail import send_problem_report

DEBUG_MODE = bool(os.environ.get('CREATE_DEBUG', ''))

conf = ConfigParser()
conf.read(os.environ['CREATE_CONFIG_FILE'])

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


creds = AccountCreationCredentials(
    **{
        field:
            conf.get(*field.split('_'))
            for field in AccountCreationCredentials._fields
    },
)

# if in debug mode, disable celery logging so that stdin / stdout / stderr
# don't get tampered with (otherwise, interactive debuggers won't work)
if DEBUG_MODE:
    def no_logging(*args, **kwargs):
        pass
    setup_logging.connect(no_logging)


def failure_handler(exc, task_id, args, kwargs, einfo):
    """Handle errors in Celery tasks by reporting via ocflib.

    We want to report actual errors, not just validation errors. Unfortunately
    it's hard to pick them out. For now, we just ignore ValueErrors and report
    everything else.

    It's likely that we'll need to revisit that some time in the future.
    """
    if isinstance(exc, ValueError):
        return

    if not DEBUG_MODE:
        try:
            send_problem_report(
                dedent(
                    """\
                An exception occured in create:

                {traceback}

                Task Details:
                  * task_id: {task_id}

                Try `journalctl -u ocf-create` for more details."""
                ).format(
                    traceback=einfo,
                    task_id=task_id,
                    args=args,
                    kwargs=kwargs,
                    einfo=einfo,
                ),
            )
        except Exception as ex:
            print(ex)  # just in case it errors again here
            send_problem_report(
                dedent(
                    """\
                An exception occured in create, but we errored trying to report it:

                {traceback}
                """
                ).format(traceback=format_exc()),
            )
            raise


tasks = get_tasks(celery, credentials=creds)
for task in tasks:
    locals()[task.__name__] = task
    task.on_failure = failure_handler
