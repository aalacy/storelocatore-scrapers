# This crawler covers the countries across `Africa` continent. The list of countries provided below:


| SN | contitent | country_name | country_code |
| --------- | --------- | ------------ | ------------ |
| 1 | AF | Algeria | DZ |
| 2 | AF | Angola | AO |
| 3 | AF | Benin | BJ |
| 4 | AF | Botswana | BW |
| 5 | AF | Burkina Faso | BF |
| 6 | AF | Burundi | BI |
| 7 | AF | Cameroon | CM |
| 8 | AF | Cape Verde | CV |
| 9 | AF | Central African Republic | CF |
| 10 | AF | Chad | TD |
| 11 | AF | Comoros | KM |
| 12 | AF | Congo | CD |
| 13 | AF | Congo | CG |
| 14 | AF | Cote d'Ivoire | CI |
| 15 | AF | Djibouti | DJ |
| 16 | AF | Egypt | EG |
| 17 | AF | Equatorial Guinea | GQ |
| 18 | AF | Eritrea | ER |
| 19 | AF | Ethiopia | ET |
| 20 | AF | Gabon | GA |
| 21 | AF | Gambia | GM |
| 22 | AF | Ghana | GH |
| 23 | AF | Guinea-Bissau | GW |
| 24 | AF | Guinea | GN |
| 25 | AF | Kenya | KE |
| 26 | AF | Lesotho | LS |
| 27 | AF | Liberia | LR |
| 28 | AF | Libyan Arab Jamahiriya | LY |
| 29 | AF | Madagascar | MG |
| 30 | AF | Malawi | MW |
| 31 | AF | Mali | ML |
| 32 | AF | Mauritania | MR |
| 33 | AF | Mauritius | MU |
| 34 | AF | Mayotte | YT |
| 35 | AF | Morocco | MA |
| 36 | AF | Mozambique | MZ |
| 37 | AF | Namibia | NA |
| 38 | AF | Niger | NE |
| 39 | AF | Nigeria | NG |
| 40 | AF | Reunion | RE |
| 41 | AF | Rwanda | RW |
| 42 | AF | Saint Helena | SH |
| 43 | AF | Sao Tome and Principe | ST |
| 44 | AF | Senegal | SN |
| 45 | AF | Seychelles | SC |
| 46 | AF | Sierra Leone | SL |
| 47 | AF | Somalia | SO |
| 48 | AF | South Africa | ZA |
| 49 | AF | South Sudan | SS |
| 50 | AF | Sudan | SD |
| 51 | AF | Swaziland | SZ |
| 52 | AF | Tanzania | TZ |
| 53 | AF | Togo | TG |
| 54 | AF | Tunisia | TN |
| 55 | AF | Uganda | UG |
| 56 | AF | Western Sahara | EH |
| 57 | AF | Zambia | ZM |
| 58 | AF | Zimbabwe | ZW |



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