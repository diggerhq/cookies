import os, sys
import json
import boto3
import tempfile
import zipfile
import uuid
from diggercookies import cookies
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def zipdir(path, ziph):
    # ziph is zipfile handle
    lenDirPath = len(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            filePath = os.path.join(root, file)
            # the second argument ensures accurate tree structure in the zip file
            ziph.write(filePath, filePath[lenDirPath:])


@app.route("/health", methods=["GET"])
def health():
    return {}

@app.route("/terraform", methods=["POST"])
def handler():


    AWS_KEY=os.environ["AWS_KEY"]
    AWS_SECRET=os.environ["AWS_SECRET"]
    target_bucket_name=os.environ["BUCKET_NAME"]
        

    # project_settings = {
    #     "app_name": "my-project",
    #     "environment": "dev",
    #     "region": "us-east-1",
    #     # "launch_type": "FARGATE"
    #     "services": {
    #         "my-service": {
    #             "service_type": "container",
    #             "service_name": "my-service",
    #             "health_check": "/",
    #             "container_port": 8080,
    #             "load_balancer": True,
    #             "task_cpu": "256",
    #             "task_memory": "1024",
    #             "internal": False,
    #         }
    #     },
    #     "environment_config": {
    #         "needs_database": True,
    #         "fargate_service_exists": True,
    #         "eks_service_exists": False,
    #         "cloudfront_service_exists": False,
    #         "lambda_service_exists": False,
    #     }
    # }
    project_settings = request.json["data"]


    with tempfile.TemporaryDirectory() as tmpdirname:

        cookies.render("https://github.com/diggerhq/target-aws", project_settings, branch="v2", output_dir=tmpdirname)

        # zipping the resulting directory
        zip_path = tempfile.mkdtemp()
        zip_path = os.path.join(zip_path, "terraform.zip")
        ziph = zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED)
        zipdir(tmpdirname, ziph)
        ziph.close()

        # upload to s3
        file_key = str(uuid.uuid1()) + ".zip"
        client = boto3.client(
            's3',
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
        )

        client.upload_file(
            zip_path,
            target_bucket_name,
            file_key,
            ExtraArgs=None,
            Callback=None,
            Config=None
        )
        
        url = client.generate_presigned_url(
                'get_object',
                Params={
                        'Bucket': target_bucket_name,
                        'Key': file_key
                    },
                ExpiresIn=3600)

    return {"url": url}


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=8888)
