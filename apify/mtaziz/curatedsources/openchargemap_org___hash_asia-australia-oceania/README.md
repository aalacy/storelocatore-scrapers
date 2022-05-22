# This covers the countries across `Asia` and `Australia and Oceania` . The list of countries provided below:


| SN | contitent | country_name | country_code |
| --------- | --------- | ------------ | ------------ |
| 1 | AS | Afghanistan | AF |
| 2 | AS | Armenia | AM |
| 3 | AS | Azerbaijan | AZ |
| 4 | AS | Bahrain | BH |
| 5 | AS | Bangladesh | BD |
| 6 | AS | Bhutan | BT |
| 7 | AS | Brunei Darussalam | BN |
| 8 | AS | Cambodia | KH |
| 9 | AS | China | CN |
| 10 | AS | Cyprus | CY |
| 11 | AS | Georgia | GE |
| 12 | AS | Hong Kong | HK |
| 13 | AS | India | IN |
| 14 | AS | Indonesia | ID |
| 15 | AS | Iran | IR |
| 16 | AS | Iraq | IQ |
| 17 | AS | Israel | IL |
| 18 | AS | Japan | JP |
| 19 | AS | Jordan | JO |
| 20 | AS | Kazakhstan | KZ |
| 21 | AS | Korea | KP |
| 22 | AS | Korea | KR |
| 23 | AS | Kuwait | KW |
| 24 | AS | Kyrgyz Republic | KG |
| 25 | AS | Lao People's Democratic Republic | LA |
| 26 | AS | Lebanon | LB |
| 27 | AS | Macao | MO |
| 28 | AS | Malaysia | MY |
| 29 | AS | Maldives | MV |
| 30 | AS | Mongolia | MN |
| 31 | AS | Myanmar | MM |
| 32 | AS | Nepal | NP |
| 33 | AS | Oman | OM |
| 34 | AS | Pakistan | PK |
| 35 | AS | Palestinian Territory | PS |
| 36 | AS | Philippines | PH |
| 37 | AS | Qatar | QA |
| 38 | AS | Saudi Arabia | SA |
| 39 | AS | Singapore | SG |
| 40 | AS | Sri Lanka | LK |
| 41 | AS | Syrian Arab Republic | SY |
| 42 | AS | Taiwan | TW |
| 43 | AS | Tajikistan | TJ |
| 44 | AS | Thailand | TH |
| 45 | AS | Timor-Leste | TL |
| 46 | AS | Turkey | TR |
| 47 | AS | Turkmenistan | TM |
| 48 | AS | United Arab Emirates | AE |
| 49 | AS | Uzbekistan | UZ |
| 50 | AS | Vietnam | VN |
| 51 | AS | Yemen | YE |
| 52 | OC | American Samoa | AS |
| 53 | OC | Australia | AU |
| 54 | OC | Cook Islands | CK |
| 55 | OC | Fiji | FJ |
| 56 | OC | French Polynesia | PF |
| 57 | OC | Guam | GU |
| 58 | OC | Kiribati | KI |
| 59 | OC | Marshall Islands | MH |
| 60 | OC | Micronesia | FM |
| 61 | OC | Nauru | NR |
| 62 | OC | New Caledonia | NC |
| 63 | OC | New Zealand | NZ |
| 64 | OC | Niue | NU |
| 65 | OC | Northern Mariana Islands | MP |
| 66 | OC | Palau | PW |
| 67 | OC | Papua New Guinea | PG |
| 68 | OC | Samoa | WS |
| 69 | OC | Solomon Islands | SB |
| 70 | OC | Tokelau | TK |
| 71 | OC | Tonga | TO |
| 72 | OC | Tuvalu | TV |
| 73 | OC | Vanuatu | VU |
| 74 | OC | Wallis and Futuna | WF |



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