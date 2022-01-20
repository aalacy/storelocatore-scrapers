# This covers US and CA. The list of countries provided below:

| SN | contitent | country_name | country_code |
| --------- | --------- | ------------ | ------------ |
| 1 | NA | Canada | CA |



# API KEY

In order to get the API Key, we have to signup at https://openchargemap.org/site and create an app. 

- https://community.openchargemap.org/t/notice-some-http-user-agents-are-now-banned-api-web/79

It is noted that `User-Agent` in `headers` must be the app name.  In this case, the app name is `Openchargemap Data`, and `headers` would be like below. 


```
headers = {
            "user-agent": "Openchargemap Data",
            }
```


# Note
If the crawler run on Apify with the US and CA as a single crawler, it experiences CSV chunking issue. 
But when this crawler for Canada without the US is run, it does not seem to experience chunking issue. 

# The following validation checks ignored
- --ignore CentroidValidator
- --ignore StreetAddressHasNumber
- --ignore StreetAddressHasStateName
- --ignore GeoConsistencyValidator
- --ignore CountryValidator
- --ignore StoreNumberColumnValidator
- --ignore LatLngDuplicationValidator