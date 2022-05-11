# North America and Sounth America except US and CA. The list of countries provided below:


| SN | contitent | country_name | country_code |
| --------- | --------- | ------------ | ------------ |
| 0 | NA | Anguilla | AI |
| 1 | NA | Antigua and Barbuda | AG |
| 2 | SA | Argentina | AR |
| 3 | NA | Aruba | AW |
| 4 | NA | Bahamas | BS |
| 5 | NA | Barbados | BB |
| 6 | NA | Belize | BZ |
| 7 | NA | Bermuda | BM |
| 8 | SA | Bolivia | BO |
| 9 | NA | Bonaire | BQ |
| 10 | SA | Brazil | BR |
| 11 | NA | British Virgin Islands | VG |
| 12 | NA | Cayman Islands | KY |
| 13 | SA | Chile | CL |
| 14 | SA | Colombia | CO |
| 15 | NA | Costa Rica | CR |
| 16 | NA | Cuba | CU |
| 17 | NA | Curaçao | CW |
| 18 | NA | Dominica | DM |
| 19 | NA | Dominican Republic | DO |
| 20 | SA | Ecuador | EC |
| 21 | NA | El Salvador | SV |
| 22 | SA | Falkland Islands (Malvinas) | FK |
| 23 | SA | French Guiana | GF |
| 24 | NA | Greenland | GL |
| 25 | NA | Grenada | GD |
| 26 | NA | Guadeloupe | GP |
| 27 | NA | Guatemala | GT |
| 28 | SA | Guyana | GY |
| 29 | NA | Haiti | HT |
| 30 | NA | Honduras | HN |
| 31 | NA | Jamaica | JM |
| 32 | NA | Martinique | MQ |
| 33 | NA | Mexico | MX |
| 34 | NA | Montserrat | MS |
| 35 | NA | Nicaragua | NI |
| 36 | NA | Panama | PA |
| 37 | SA | Paraguay | PY |
| 38 | SA | Peru | PE |
| 39 | NA | Puerto Rico | PR |
| 40 | NA | Saint Barthelemy | BL |
| 41 | NA | Saint Kitts and Nevis | KN |
| 42 | NA | Saint Lucia | LC |
| 43 | NA | Saint Martin | MF |
| 44 | NA | Saint Pierre and Miquelon | PM |
| 45 | NA | Saint Vincent and the Grenadines | VC |
| 46 | NA | Sint Maarten (Netherlands) | SX |
| 47 | SA | Suriname | SR |
| 48 | NA | Trinidad and Tobago | TT |
| 49 | NA | Turks and Caicos Islands | TC |
| 50 | NA | United States Virgin Islands | VI |
| 51 | SA | Uruguay | UY |
| 52 | SA | Venezuela | VE |



# API KEY

In order to get the API Key, we have to signup at https://openchargemap.org/site and create an app. 

- https://community.openchargemap.org/t/notice-some-http-user-agents-are-now-banned-api-web/79

It is noted that `User-Agent` in `headers` must be the app name.  In this case, the app name is `Openchargemap Data`, and `headers` would be like below. 


```
headers = {
            "user-agent": "Openchargemap Data",
            }
```



# The following validation checks ignored
- --ignore CentroidValidator
- --ignore StreetAddressHasNumber
- --ignore StreetAddressHasStateName
- --ignore GeoConsistencyValidator
- --ignore CountryValidator
- --ignore StoreNumberColumnValidator
- --ignore LatLngDuplicationValidator