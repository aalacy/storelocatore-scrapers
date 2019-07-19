from setuptools import setup, find_packages

setup(
    name='sgvalidator',
    version="0.0.8",
    author="noah",
    author_email="info@safegraph.com",
    packages=find_packages(),
    test_suite='nose.collector',
    include_package_data=True,
    tests_require=['nose'],
    install_requires=[
        "termcolor==1.1.0",
        "phonenumbers==8.10.13",
        "zipcodes==1.0.5",
        "us==1.0.0",
        "pandas"  # no need to pin this to a specific version
    ],
    zip_safe=False
)
