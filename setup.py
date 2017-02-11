from setuptools import find_packages
from setuptools import setup

try:
    with open('.version') as f:
        VERSION = f.readline().strip()
except IOError:
    VERSION = 'unknown'

setup(
    name='create',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    url='https://www.ocf.berkeley.edu/',
    author='Open Computing Facility',
    author_email='help@ocf.berkeley.edu',
    install_requires=[
        # TODO: stop using our fork
        # https://github.com/celery/celery/pull/3831
        'ckuehl-celery[redis]==4.0.2.post1',
        'ocflib',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': {
            'create-worker = create.worker:main',
            'approve = create.approve:main',
        },
    },
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
