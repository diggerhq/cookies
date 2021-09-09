import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock
from diggercookies import cookies


example_project = {
    "app_name": "my-project",
    "environment": "dev",
    "region": "us-east-1",
    # "launch_type": "FARGATE"
    "services": {
        "my-service": {
            "service_type": "container",
            "service_name": "my-service",
            "health_check": "/",
            "container_port": 8080,
            "load_balancer": True,
            "task_cpu": "256",
            "task_memory": "1024",
            "internal": False,
        }
    },
    "environment_config": {
        "needs_database": True,
        "fargate_service_exists": True,
        "eks_service_exists": False,
        "cloudfront_service_exists": False,
        "lambda_service_exists": False,
    }
}

class TestAWSRendering(unittest.TestCase):
    def test_with_file_and_no_overrides(self):
        global example_project
        with tempfile.TemporaryDirectory() as tmpdirname:
            cookies.render("https://github.com/diggerhq/target-aws", example_project, branch="v2", output_dir="/tmp/aws")