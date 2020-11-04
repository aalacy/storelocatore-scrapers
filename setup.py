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
            "black==20.8b1",
            "flake8==3.8.4",
            "mypy==0.790",
            "mypy-extensions==0.4.3",
        ]
    },
)
