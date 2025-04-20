from pathlib import Path

from transpire.resources import Deployment, Secret, Service
from transpire.types import Image, ContainerRegistry
from transpire.utils import get_image_tag

name = "create"
auto_sync = True


def images():
    yield Image(name="create", path=Path("/"), registry=ContainerRegistry("ghcr"))


def add_probes(dep):
    dep.obj.spec.template.spec.containers[0].readiness_probe = {
        "exec": {
            "command": ["python", "-m", "create.healthcheck"],
        },
        "initialDelaySeconds": 15,
        "periodSeconds": 15,
    }

    dep.obj.spec.template.spec.containers[0].liveness_probe = {
        "exec": {
            "command": ["python", "-m", "create.healthcheck"],
        },
        "initialDelaySeconds": 15,
        "periodSeconds": 15,
    }


def add_volumes(dep):
    dep.obj.spec.template.spec.volumes = [
        {"name": "nfs-export-home", "nfs": {"path": "/opt/homes/home", "server": "homes.ocf.berkeley.edu"}},
        {"name": "nfs-export-services", "nfs": {"path": "/opt/homes/services", "server": "services.ocf.berkeley.edu"}},
        {"name": "secrets", "secret": {"secretName": "create"}},
    ]

    dep.obj.spec.template.spec.containers[0].volume_mounts = [
        {"name": "nfs-export-home", "mountPath": "/home"},
        {"name": "nfs-export-services", "mountPath": "/services"},
        {"name": "secrets", "mountPath": "/etc/ocf-create"},
    ]


def objects():
    dep = Deployment(
        name="create",
        image=get_image_tag("create"),
        ports=[6378],
    )

    dep.obj.spec.template.spec.dns_policy = "ClusterFirst"
    dep.obj.spec.template.spec.dns_config = {"searches": ["ocf.berkeley.edu"]}

    add_probes(dep)
    add_volumes(dep)

    svc = Service(
        name="create",
        selector=dep.get_selector(),
        port_on_pod=6378,
        port_on_svc=6378,
    )

    sec = Secret(
        name="create",
        string_data={
            "create.key": "",
            "create-keytab-base64": "",
            "create.pub": "",
            "create-redis-base64": "",
            "ocf-create.conf": "",
        },
    )

    yield dep.build()
    yield svc.build()
    yield sec.build()
