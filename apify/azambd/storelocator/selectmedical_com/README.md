# Description

Crawl is now missing approx 275 locations (almost all w/location_type = "Outpatient Rehab"). There should be 1,899 locations per https://www.selectmedical.com/locations/#g=&o=&services=&a= (when checking all boxes).
Please also add page_url column to this crawl.

## QA msg on previous version:

- Previous row count was 1860 and currently its 1769.
  While website shows 1900 locations, Kindly confirm the count.

- 1760 locations for now, Please check why 200+ locations are missing.

## after rewrite: 
- Got 1900 locations 

Missing 08 rows which are invalid b/c Lat/Lon=0

| id                                   | location name                                                           |
| ------------------------------------ | ----------------------------------------------------------------------- |
| 22ec8bcf-8a22-4984-b10d-38d70026894a | MISSING                                                                 |
| 53a8b5ed-64e3-4cdf-82f3-07994e6bfb76 | MISSING                                                                 |
| 0f7004b6-a09d-4e63-9305-d46b46145bfa | MISSING                                                                 |
| 3f653c0c-46c6-4161-aebc-e4d9723c2077 | MISSING                                                                 |
| e5f04c70-d2c6-4e43-b53e-1fdf080b9723 | MISSING                                                                 |
| d137d60a-a173-4f08-8275-ded0aef9452d | MISSING                                                                 |
| beeda9fc-f10a-4d7c-930f-40caa0804e4c | MISSING                                                                 |
| be065f17-d4f4-4a2a-85f9-aaee56e4fd5a | MISSING                                                                 |


> There is no SUCCESS file as multiple duplicates Lat/Lon , checked myself data is valid