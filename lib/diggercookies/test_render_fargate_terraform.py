import os
import random
import shutil
import string
from pathlib import Path

from lib.diggercookies.cookies import render


def test_render_fargate_template():
    repo = "git@github.com:diggerhq/target-fargate.git"

    letters = string.ascii_lowercase
    random_str = ''.join(random.choice(letters) for i in range(6))
    target_dir = f"{Path.home()}/tmp/{random_str}"

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
    }

    render(repo, "add-nat-gateway", options, output_dir=target_dir)

