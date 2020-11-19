
validate.py data.csv --ignore CentroidValidator --ignore CountryValidator --ignore StoreNumberColumnValidator --ignore LatLngDuplicationValidator

All data scraped from API. This may contain duplicates (already deduped) or odd data, however this is correct.

613     49.8   -97.164  EITHER_LAT_OR_LNG_IMPRECISE        613
192           Manitoba   <MISSING>  R0I 1Z0  INVALID_CA_POSTAL_CODE        192
561       Saskatchewan  3063433403  S7N 4MB  INVALID_CA_POSTAL_CODE        561
737             Quebec   450652809  J3X 1N9        INVALID_CA_PHONE        737
1245  British Columbia   <MISSING>  V9I 4T8  INVALID_CA_POSTAL_CODE       1245
259    43.664265   -79.733718  {Jean-Talon Est, 4325, Boul. St-Martin Ouest, ...         35
684   45.4393606  -73.6913987  {Boulevard Saint Jean Baptiste,, 114, Boulevar...         25
620     45.29715    -74.17829  {235, rte. 338, , 235, rte. 338, 235, Â Route ...          3
252     43.66087   -79.328424  {Dupont St, 650, Bayview Avenue, 2877, 17 Lesl...          3
1293   51.793675  -114.134711  {100-6509 46th St, , 100-6509 46th St, #300 - ...          3
979    47.821226   -69.504122     {342, ch. Temiscouata, , 342, ch. Temiscouata}          2
1072    49.17935     -123.138                    {4651 No.3 Road, , 4651 No3 Rd}          2
1047   49.090992  -117.635286  {142-8100 Rock Island Hwy, , 142-8100 Rock Isl...          2
1031     48.8918      -72.202     {224, boul. St-Michel, 224, boul. St-Michel, }          2
1023     48.7442     -69.0865  {25, Route 138,  C.P. 100, , 25, rte. 138, CP ...          2
     street_address  same_lat_count  same_lng_count
391     165 Main St               2               2
921  40 Meredith St               2               2


←[31mStore number column contains 168 duplicates. Here are a few examples of store numbers which appear at least twice i
n your data: ['2809' '8384' '8878' '0096' '8958']←[0m



# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
