# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore LatLngDuplicationValidator --ignore CentroidValidator --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName --ignore GeoConsistencyValidator --ignore CountryValidator

160   39.7406    -121.8  EITHER_LAT_OR_LNG_IMPRECISE        160
306   39.3073    -123.8  EITHER_LAT_OR_LNG_IMPRECISE        306
703   21.4104    -158.0  EITHER_LAT_OR_LNG_IMPRECISE        703
1150  43.8219     -83.1  EITHER_LAT_OR_LNG_IMPRECISE       1150
1444  40.7213     -73.3  EITHER_LAT_OR_LNG_IMPRECISE       1444
453   5990 Kingstowne Towne Center  ADDR_HAS_NO_NUMBER        453
1186              Highway 210 & 78  ADDR_HAS_NO_NUMBER       1186
1188          Highway 60,  Box 358  ADDR_HAS_NO_NUMBER       1188
1233              Highway 65 South  ADDR_HAS_NO_NUMBER       1233
1241  Rt 1,  Box 1112,  Highway 64  ADDR_HAS_NO_NUMBER       1241
592  31031 Avenue A,  US 1  ADDR_CONTAINS_STATE_NAME        592
36  96931    GU  ZIPCODE_NOT_IN_STATE         36
1062    MA   +1.  01571  INVALID_US_PHONE       1062
1265    MT   +1.  59715  INVALID_US_PHONE       1265
1604    OH   +1.  45810  INVALID_US_PHONE       1604
1725    RI   +1.  02889  INVALID_US_PHONE       1725
1726    RI   +1.  02909  INVALID_US_PHONE       1726
(I replaced the '.' in phones for this one.. also the +1)
56    26.983322   -82.144991          {1680 El Jobean Road, 1680 El Jobean Rd.}          2
369   33.294108   -83.965048            {935 Stark Rd., 110 South Harkness St.}          2
980   39.080461  -108.541256                {2755 North Avenue, 2808 North Ave}          2
1283  40.844984   -73.843255  {1644 Mayflower Avenue, 3396 East Tremont Avenue}          2
1849   44.98188    -92.69082           {625 Commerce Drive, 906 Dominion Drive}          2
1877  45.642953  -122.675812        {500 W. 8th St., 400 East Mill Plain Blvd.}          2
(I deduped, this is just their problem)
158   111 Main Street               2               2
922   270 Main Street               2               2
1212  404 Main Street               2               2
1297   44 Main Street               2               2
1411  506 Main Street               2               2

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
