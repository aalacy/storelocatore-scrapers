# This covers Europe ( EU ) except FR, IT, NL, DE, and GB. The list of countries provided below:


| SN | contitent | country_name | country_code |
| --------- | --------- | ------------ | ------------ |
| 1 | EU | Åland Islands | AX |
| 2 | EU | Albania | AL |
| 3 | EU | Andorra | AD |
| 4 | EU | Armenia | AM |
| 5 | EU | Austria | AT |
| 6 | EU | Azerbaijan | AZ |
| 7 | EU | Belarus | BY |
| 8 | EU | Belgium | BE |
| 9 | EU | Bosnia and Herzegovina | BA |
| 10 | EU | Bulgaria | BG |
| 11 | EU | Croatia | HR |
| 12 | EU | Cyprus | CY |
| 13 | EU | Czech Republic | CZ |
| 14 | EU | Denmark | DK |
| 15 | EU | Estonia | EE |
| 16 | EU | Faroe Islands | FO |
| 17 | EU | Georgia | GE |
| 18 | EU | Gibraltar | GI |
| 19 | EU | Greece | GR |
| 20 | EU | Guernsey | GG |
| 21 | EU | Holy See (Vatican City State) | VA |
| 22 | EU | Hungary | HU |
| 23 | EU | Iceland | IS |
| 24 | EU | Ireland | IE |
| 25 | EU | Isle of Man | IM |
| 26 | EU | Jersey | JE |
| 27 | EU | Kazakhstan | KZ |
| 28 | EU | Latvia | LV |
| 29 | EU | Liechtenstein | LI |
| 30 | EU | Lithuania | LT |
| 31 | EU | Luxembourg | LU |
| 32 | EU | Macedonia | MK |
| 33 | EU | Malta | MT |
| 34 | EU | Moldova | MD |
| 35 | EU | Monaco | MC |
| 36 | EU | Montenegro | ME |
| 37 | EU | Norway | NO |
| 38 | EU | Poland | PL |
| 39 | EU | Portugal | PT |
| 40 | EU | Romania | RO |
| 41 | EU | Russian Federation | RU |
| 42 | EU | San Marino | SM |
| 43 | EU | Serbia | RS |
| 44 | EU | Slovakia (Slovak Republic) | SK |
| 45 | EU | Slovenia | SI |
| 46 | EU | Spain | ES |
| 47 | EU | Svalbard & Jan Mayen Islands | SJ |
| 48 | EU | Sweden | SE |
| 49 | EU | Switzerland | CH |
| 50 | EU | Turkey | TR |
| 51 | EU | Ukraine | UA |



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