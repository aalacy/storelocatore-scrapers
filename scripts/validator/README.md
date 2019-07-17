To run tests:

`python setup.py test`

After a change is made, just run: 

`[sudo] pip install validator/`

Note: the "/" is *very* important and pip won't override past installs unless you include it!

Make sure you've activated a [virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/), 
or else this package will be installed globally.

### ToDo:
* Failing on empty dir
* Values that contain "null"
* Maybe using pandas in the data checker?
* sometimes you see “San Francisco null” or null in every street address
* Html snippets - “chicago <span”
* For counts: hardcode a list of counts by brand_id using M&M and then check counts against that (raw ingest counts, not post pipeline counts)
* If column is all blank - “are you sure this is all missing?”
