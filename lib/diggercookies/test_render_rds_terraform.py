import os
import pathlib
import random
import shutil
import string
from pathlib import Path

from lib.diggercookies.cookies import render


def test_render_rds_template():
    repo = "git@github.com:diggerhq/resources-template.git"
    random_str = "rds"
    target_dir = f"{Path.home()}/tmp/{random_str}"

    # delete dir first
    p = pathlib.Path(target_dir)
    if p.exists():
        shutil.rmtree(p)

    options = {
        "app_name": "",
        "environment": "",
        "launch_type": "",
        "environment_config": {"disable_nat": True},
        "monitoring_enabled": "True",
        "services": {
            "x": {
                "service_name": "x",
                "service_type": "container",
                "standalone_task": True,
            }
        },
        "resources": {
            "y": {
                "resource_type": "database",
                "rds_instance_class": "db.t3.micro",
                "rds_engine": "mysql",
                "rds_engine_version": "5.7",
                "rds_allocated_storage": "5",
            }
        }
    }

    render(repo, "feat/support-rds", options, output_dir=target_dir)

