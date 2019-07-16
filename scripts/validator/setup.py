import validator
from setuptools import setup, find_packages

setup(
    name='validator',
    version=validator.__version__,
    description='validates store locator data',
    url='https://github.com/SafeGraphInc/crawl-service',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False
)