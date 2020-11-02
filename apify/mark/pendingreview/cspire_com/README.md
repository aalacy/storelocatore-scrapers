New validator is flagging two errors.

Error1:

Found 2 <lat, lng> pair(s) that belong to multiple addresses. Examples:
   latitude longitude                                     street_address  num_addrs
63    32.34   -90.065                    {375 Ridgeway , 369 Ridge Way }          2
71     32.4   -90.131  {230 E. County Line Road Suite F, 201 Ring Roa...          2

Reason: These lat / lng pairs are pulled from the google maps provided. I've also attempted to use the JSON data they provide, which yields a different result.

Error2:

We found 6 rows with bad centroids. Look at the REASON column in the output below to see why these rows were flagged. 
Note: if you see `EITHER_LAT_OR_LNG_IMPRECISE`, that means that either your latitude or longitude has fewer than 2 significant figures (i.e. the number of digits trailing the dot). Examples:
                        location_name                   street_address  ... longitude                       REASON
4                             CellPro         1250 E County Line Road   ...    -90.13  EITHER_LAT_OR_LNG_IMPRECISE
8                   Wireless Wizard 1  230 E. County Line Road Suite F  ...   -90.131  EITHER_LAT_OR_LNG_IMPRECISE
49  Bay Springs Select Retail - WiCom                   9K Bay Avenue   ...     -89.3  EITHER_LAT_OR_LNG_IMPRECISE
50                             Laurel              1203 Highway 15 N.   ...   -89.147  EITHER_LAT_OR_LNG_IMPRECISE
88                      Ocean Springs        2424 Bienville Boulevard   ...     -88.8  EITHER_LAT_OR_LNG_IMPRECISE

[5 rows x 5 columns]

Reason: I've attempted using both the JSON data they provide and the values directly from the google maps link. Sometimes they don't provide a more accurate result. All points are pulled based on what they've provided. 