# NOTE: crawl-service is not installable as a library. This file is
# currently only used to specify development dependencies.

from setuptools import setup

package = "pub-crawl"
version = "0.1"

setup(
    name=package,
    version=version,
    description="",
    url="https://github.com/SafeGraphInc/crawl-service",
    extras_require={
        "dev": [
            "black==22.3.0",
            "flake8==3.8.4",
            "flake8-eradicate==1.0.0",
            "flake8-requirements==1.3.3",
            "flake8-safegraph-crawl==0.4",
            "mypy==0.790",
            "mypy-extensions==0.4.3",
            "piprot==0.9.11",
        ]
    },
)
