import os
import glob
import subprocess
from jinja2 import Template
import tempfile
import logging


class ServiceType:
    CONTAINER = "container"
    SERVERLESS = "serverless"
    WEBAPP = "webapp"


def clone_gh_repo(url, ref, path="."):
    if ref is None:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth", "1",
                url, path
            ],
            check=True
        )
    else:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth", "1",
                "--branch", ref,
                url, path
            ],
            check=True
        )


def service_config_overrides(environment_config_options, service_name):
    overrided_options = environment_config_options.copy()
    for key,value in environment_config_options.items():
        if key.startswith(f"service.{service_name}"):
            override_key = key.replace(f"service.{service_name}.", "")
            overrided_options[override_key] = value
        if key.startswith("service."):
            overrided_options.pop(key)
    return overrided_options


def render_jinja_template(terraformOptions, inputFile, outputFile, delete_original=False):
    tvars_file = open(inputFile)
    tvars_content = tvars_file.read()
    tvars_template = Template(tvars_content)
    tvars_content_rendered = tvars_template.render(terraformOptions)

    tvars_file_output = open(f"{outputFile}", "w")
    tvars_file_output.write(tvars_content_rendered)
    tvars_file_output.close()
    tvars_file.close()
    os.remove(inputFile)


def _render(options, path=".", output_dir=None):
    tfvars_template_file_name = os.path.join(path, "terraform.template.tfvars")
    tvars_file_name = os.path.join(path, "terraform.tfvars")
    # backendTemplateFileName = os.path.join(path, "backend_s3.template.conf")
    # backendFileName = os.path.join(path, "backend_s3.conf")
    render_jinja_template(options, tfvars_template_file_name, tvars_file_name)
    # render_jinja_template(backend_options, backendTemplateFileName, backendFileName)

    # Render service file
    path = os.path.abspath(path)
    template_main_dir = os.path.join(path, "main/")

    service_template_file_name = os.path.join(template_main_dir, "service.template.tf")
    service_fargate_template_file_name = os.path.join(template_main_dir, "service-fargate.template.tf")
    service_eks_template_file_name = os.path.join(template_main_dir, "service-eks.template.tf")
    service_lambda_template_file_name = os.path.join(template_main_dir, "service-lambda.template.tf")
    service_webapp_template_file_name = os.path.join(template_main_dir, "service-webapp.template.tf")
    for _, service_options in options["services"].items():
        service_name = service_options["service_name"]
        service_type = service_options["service_type"]

        # this template does not support webapps
        if service_type == ServiceType.WEBAPP and \
                not os.path.exists(service_webapp_template_file_name):
            continue

        service_options["app_name"] = options["app_name"]
        service_options["environment"] = options["environment"]
        service_options["launch_type"] = options.get("launch_type", "FARGATE")
        # also include environment config with service-specific overrides
        service_environment_options = service_config_overrides(options["environment_config"], service_name)
        service_options["environment_config"] = service_environment_options
        service_file_name = os.path.join(path, f"main/service-{service_name}.tf")

        # a hacky way to make our rending engine work with both older templates which use "service.template.tf"
        # and newer template which are using service-lambda, service-fargate and service-eks targets
        if service_type == ServiceType.WEBAPP:
            source_template_file_name = service_webapp_template_file_name
        elif service_type == ServiceType.SERVERLESS and os.path.exists(service_lambda_template_file_name):
            source_template_file_name = service_lambda_template_file_name
        elif service_type == ServiceType.CONTAINER and os.path.exists(service_fargate_template_file_name) \
                and service_options["environment_config"].get("fargate_service_exists", False):
            source_template_file_name = service_fargate_template_file_name
        elif service_type == ServiceType.CONTAINER and os.path.exists(service_eks_template_file_name) \
                and service_options["environment_config"].get("eks_service_exists", False):
            source_template_file_name = service_eks_template_file_name
        else:
            source_template_file_name = service_template_file_name

        render_jinja_template(service_options, source_template_file_name, service_file_name)

    try:
        os.remove(service_template_file_name)
    except OSError:
        logging.warning(f"Failed to remove {service_template_file_name}")
        pass

    try:
        os.remove(service_fargate_template_file_name)
    except OSError:
        logging.warning(f"Failed to remove {service_fargate_template_file_name}")
        pass

    try:
        os.remove(service_eks_template_file_name)
    except OSError:
        logging.warning(f"Failed to remove {service_eks_template_file_name}")
        pass

    try:
        os.remove(service_lambda_template_file_name)
    except OSError:
        logging.warning(f"Failed to remove {service_lambda_template_file_name}")
        pass

    try:
        os.remove(service_webapp_template_file_name)
    except OSError:
        logging.warning(f"Failed to remove {service_webapp_template_file_name}")
        pass

    for templateFile in glob.glob(os.path.join(template_main_dir, "*.template.tf")):
        terraform_file_name = templateFile.replace(".template.tf", ".tf")
        render_jinja_template(options, templateFile, terraform_file_name)


def render(repo_url, branch, options, output_dir):
    try:
        clone_gh_repo(repo_url, branch, path=output_dir)
        _render(options, path=output_dir)
    except Exception as e:
        logging.error(f"Failed to render terraform, exception: {e}")
        raise e




