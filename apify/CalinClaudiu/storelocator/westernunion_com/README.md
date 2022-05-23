# validate.py --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName --ignore GeoConsistencyValidator

# Duplicate row:

234  Clinic Pharmacy  1025 W Trinity Mills  Carrollton    TX  75006           US      Pharmacy

Actual complete data:
page_url|location_name|street_address|city|state|zip|country_code|store_number|phone|location_type|latitude|longitude|locator_domain|hours_of_operation|raw_address
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
http://www.walmart.com/store/2625 | Clinic Pharmacy | 1025 W Trinity Mills | Carrollton | TX | 75006 | US | 2625 | 800-273-3455 | Pharmacy | 32.982646 | -96.910225 | https://www.walmart.com/ | Montofrihrs: 07:00-19:00; Sundayhrs: Closed; Saturdayhrs: 09:00-13:00; Temporaryhours: <MISSING> | <MISSING>
http://www.walmart.com/store/8899 | Clinic Pharmacy | 1025 W Trinity Mills | Carrollton | TX | 75006 | US | 8899 | 800-508-0960 | Pharmacy | 32.982646 | -96.910225 | https://www.walmart.com/ | Montofrihrs: 08:00-18:00; Sundayhrs: Closed; Saturdayhrs: Closed; Temporaryhours: <MISSING> | <MISSING>
___

432                           Route 513 And I78  ADDR_HAS_NO_NUMBER        432
713                                 Rr 4 Box 82  ADDR_HAS_NO_NUMBER        713
816  Plaza Cayey 102 8000 Ave. Jesus T. PiÃ±ero  ADDR_HAS_NO_NUMBER        816
818                 Carr 167 Km 17.6 Bo Pajaros  ADDR_HAS_NO_NUMBER        818
819          Carr #2 Sector La Virgencita Inter  ADDR_HAS_NO_NUMBER        819

#### Puerto rico locations ↑↑↑↑↓↓↓↓↓

831          Ave. Los Veteranos Km 134.7  ADDR_CONTAINS_STATE_NAME        831
837                     Carr Pr 31 Km 24  ADDR_CONTAINS_STATE_NAME        837
838  Plaza Canovanas Hwy 3 Int New Rt 66  ADDR_CONTAINS_STATE_NAME        838
___

412   88570    NJ  ZIPCODE_NOT_IN_STATE        412
2766  75036    TX  ZIPCODE_NOT_IN_STATE       2766

#### Data from API, checked and crawled correctly.

