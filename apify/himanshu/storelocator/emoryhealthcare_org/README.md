--ignore StreetAddressHasNumber (Confirmed scrape correctly)
Found 4 concerning rows. Examples:
       street_address              REASON  rowNumber
352  315 Boulevard NE  ADDR_HAS_NO_NUMBER        352
357  315 Boulevard NE  ADDR_HAS_NO_NUMBER        357
615  285 Boulevard NE  ADDR_HAS_NO_NUMBER        615
633  315 Boulevard NE  ADDR_HAS_NO_NUMBER        633


--ignore GeoConsistencyValidator (Confirmed scrape correctly)
Found 3 concerning rows. Examples:
         zip state                REASON  rowNumber
279  2215752    GA  ZIPCODE_NOT_IN_STATE        279
349    30880    GA  ZIPCODE_NOT_IN_STATE        349
565    03121    GA  ZIPCODE_NOT_IN_STATE        565

--ignore CountryValidator (Confirmed scrape correctly)
Found 1 concerning rows. Examples:
    state         phone      zip          REASON  rowNumber
279    GA  404-778-7777  2215752  INVALID_US_ZIP        279

--ignore LatLngDuplicationValidator (Confirmed scrape correctly)
Found 17 <lat, lng> pair(s) that belong to multiple addresses. Examples:
     latitude  longitude                                     street_address  num_addrs
210  33.79119  -84.28578  {2665 N Decatur Rd, 2665 N. Decatur Road, 2665...          4
184  33.78038  -84.33604  {705 Town Blvd, 2200 Peachtree Rd NW, 1060 Win...          3
219   33.7927   -84.2799       {2801 N Decatur Rd, 2801 North Decatur Road}          2
478    34.066  -84.17611  {21 Ortho Lane, 6335 Hospital Pkwy, Physicians...          2
433  34.00321  -84.15876  {3400 McClure Bridge Rd, 11539 Park Woods Circle}          2
361   33.9097  -84.35029  {5671 Peachtree Dunwoody Rd, 5665 Peachtree Du...          2
312  33.86678  -84.09646  {4120 Five Fork-Trickum Road, 4120 Five Fork T...          2