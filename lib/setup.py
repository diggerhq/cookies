from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='diggercookies',
    author="Mohamed Habib",
    author_email="mo@digger.dev",
    description="Terraform cookiecutter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "jinja2==3.0.1",
        "requests==2.26.0"
    ],
    version="0.1.0",
    url="https://cookies.digger.dev",
    py_modules=["diggercookies",],
    packages=['diggercookies', ],
    entry_points='''
        [console_scripts]
        igm=infragenie.genie:cli
    '''
)
