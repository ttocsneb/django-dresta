from os import path
from setuptools import setup, find_packages


directory = path.abspath(path.dirname(__file__))


def description():
    description_file = path.join(
        directory, "README.md"
    )
    with open(description_file, encoding='utf-8') as f:
        return f.read()


INSTALL_REQUIRES = [
    'django>=3.0.7',
    'marshmallow>=3.9.1'
]

setup(
    name="django-dresta",
    version="0.1.2",

    description="Django Decorated ReST API",
    long_description=description(),
    long_description_content_type="text/markdown",

    install_requires=INSTALL_REQUIRES,

    author='Benjamin Jacobs',
    author_email='benjammin1100@gmail.com',
    url='https://github.com/ttocsneb/',

    packages=find_packages(),
    include_package_data=True
)
