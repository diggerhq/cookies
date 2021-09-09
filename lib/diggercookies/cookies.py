import os, sys, glob
import subprocess
from jinja2 import Template
import tempfile


class ServiceType:
    CONTAINER  = "container"
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
    tvarsFile = open(inputFile)
    tvarsContent = tvarsFile.read()
    tvarsTemplate = Template(tvarsContent)
    tvarsContentRendered = tvarsTemplate.render(terraformOptions)

    tvarsFileOutput = open(f"{outputFile}", "w")
    tvarsFileOutput.write(tvarsContentRendered)
    tvarsFileOutput.close()
    tvarsFile.close()

    os.remove(inputFile)


def _render(options, path=".", output_dir=None):
    tfvarsTemplateFileName = os.path.join(path, "terraform.template.tfvars")
    tvarsFileName = os.path.join(path, "terraform.tfvars")
    # backendTemplateFileName = os.path.join(path, "backend_s3.template.conf")
    # backendFileName = os.path.join(path, "backend_s3.conf")
    render_jinja_template(options, tfvarsTemplateFileName, tvarsFileName)
    # render_jinja_template(backend_options, backendTemplateFileName, backendFileName)

    # Render service file
    path = os.path.abspath(path)
    templateMainDir = os.path.join(path, "main/")

    serviceTemplateFileName = os.path.join(templateMainDir, "service.template.tf")
    serviceFargateTemplateFileName = os.path.join(templateMainDir, "service-fargate.template.tf")
    serviceEKSTemplateFileName = os.path.join(templateMainDir, "service-eks.template.tf")
    serviceLambdaTemplateFileName = os.path.join(templateMainDir, "service-lambda.template.tf")
    serviceWebappTemplateFileName = os.path.join(templateMainDir, "service-webapp.template.tf")
    for _, service_options in options["services"].items():
        serviceName = service_options["service_name"]
        serviceType = service_options["service_type"]

        # this template does not support webapps
        if serviceType == ServiceType.WEBAPP and \
                not os.path.exists(serviceWebappTemplateFileName):
            continue

        service_options["app_name"] = options["app_name"]
        service_options["environment"] = options["environment"]
        service_options["launch_type"] = options.get("launch_type", "FARGATE")
        # also include environment config with service-specific overrides
        service_environment_options = service_config_overrides(options["environment_config"], serviceName)
        service_options["environment_config"] = service_environment_options
        serviceFileName = os.path.join(path, f"main/service-{serviceName}.tf")

        # a hacky way to make our rending engine work with both older templates which use "service.template.tf"
        # and newer template which are using service-lambda, service-fargate and service-eks targets
        if serviceType == ServiceType.WEBAPP:
            sourceTemplateFileName = serviceWebappTemplateFileName
        elif serviceType == ServiceType.SERVERLESS and os.path.exists(serviceLambdaTemplateFileName):
            sourceTemplateFileName = serviceLambdaTemplateFileName
        elif serviceType == ServiceType.CONTAINER and os.path.exists(serviceFargateTemplateFileName) \
                and service_options["environment_config"].get("fargate_service_exists", False):
            sourceTemplateFileName = serviceFargateTemplateFileName
        elif serviceType == ServiceType.CONTAINER and os.path.exists(serviceEKSTemplateFileName) \
                and service_options["environment_config"].get("eks_service_exists", False):
            sourceTemplateFileName = serviceEKSTemplateFileName
        else:
            sourceTemplateFileName = serviceTemplateFileName

        render_jinja_template(service_options, sourceTemplateFileName, serviceFileName)


    try:
        os.remove(serviceTemplateFileName)
    except OSError:
        pass

    try:
        os.remove(serviceFargateTemplateFileName)
    except OSError:
        pass

    try:
        os.remove(serviceEKSTemplateFileName)
    except OSError:
        pass

    try:
        os.remove(serviceLambdaTemplateFileName)
    except OSError:
        pass

    try:
        os.remove(serviceWebappTemplateFileName)
    except OSError:
        pass


    for templateFile in glob.glob(os.path.join(templateMainDir, "*.template.tf")):
        terraformFileName = templateFile
        terraformFileName = terraformFileName.replace(".template.tf", ".tf")
        render_jinja_template(options, templateFile, terraformFileName)


def render(repo_url, options, branch="master", output_dir=None):
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = tmpdirname
        cdir = os.getcwd()
        if output_dir is None:
            output_dir = cdir

        os.chdir(output_dir)

        try:
            clone_gh_repo(repo_url, branch, path=output_dir)
            _render(options, path=output_dir)
        except Exception as e:
            os.chdir(cdir)
            raise e

        os.chdir(cdir)



