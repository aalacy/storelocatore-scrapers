#### To run tests:

`python setup.py test`

#### To upload to PyPi 

Run the upload script via:

`sh upload_to_pypi.sh`

You'll be prompted for our PyPi username and password, which you can get from Noah if you don't already have it. 

Make sure you've activated a [virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) when you run `pip install`, or else this package will be installed globally.

Then, once you're ready to install, just run:

`pip install sgvalidator` 

### ToDo:
* Maybe using pandas in the data checker?
* For counts: hardcode a list of counts by brand_id using M&M and then check counts against that (raw ingest counts, not post pipeline counts)