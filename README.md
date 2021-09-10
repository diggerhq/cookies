Introduction
============

Cookies is a project inspired by [python cookiecutter](https://github.com/cookiecutter/cookiecutter) but used for terraform generation.

**How to run your terraform**

After you download your terraform unzip the folder. You then need to go into the main folder:

```jsx
cd <terraform>/main
```

After that you can run terraform init. This step will ask you for your aws keys:

```jsx
terraform init --var-file=../terraform.tfvars
```

And finally terraform plan to see what resources will be created

```jsx
terraform plan --var-file=../terraform.tfvars
```

Once it all looks good you can run terraform apply to create your infra!

```jsx
terraform apply --var-file=../terraform.tfvars
```

**How to deploy your container app**

- Instructions coming soon

**How to deploy your web app**

- instructions coming soon

**How to deploy your lambda app**

- instructions coming soon