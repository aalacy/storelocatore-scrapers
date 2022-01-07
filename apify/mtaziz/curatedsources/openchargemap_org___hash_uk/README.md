
# NOTE

There are some issues that regards to the address data such as `city` and `street_address` in the scraped data. For example, the `city` data for some stores in the scraped data are found to be incorrect. If we look at the `city` data, it turns out to be street_address like `600 Blandford Road`. This is due to the fact that that's how the data is structured on the source page. The reason behind this might be with lack of the data validation enforcement while inserting the data by the end user.  What about correcting those incorrect data? Since the data on the source could be updated or changed or corrected by the end user in the future, applying customization on such addresses might cause the crawler stop working therefore, we have left those addresses as it is on the source page though those are not correct. 




# The list of countries provided below:


| contitent | country_name | country_code |
| --------- | ------------ | ------------ |
| EU | United Kingdom of Great Britain & Northern Ireland | GB |


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