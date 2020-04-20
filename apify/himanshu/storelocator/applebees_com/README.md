This API uses CloudFlare, which blocks requests that aren’t using the latest TLS protocol and ciphers. I was able to get around it reliably using the same approach as with gamestop.com, namely using http.client instead of the requests module, and making sure python is using an updated OpenSSL.  

To call the API we have to visit https://www.applebees.com/en/restaurants and get two hidden inputs from the form with action=”/api/sitecore/Locations/LocationSearchAsync”:

`<input id="LocationRoot" name="LocationRoot" type="hidden" value="{3B216C7F-CB81-4126-A2CE-33AD79B379CF}">`

`<input name="__RequestVerificationToken" type="hidden" value="gTmhdx1hoMbPjD3fwb335AI44-o3r1AziE7248WQhQvL2cJxNS1C20MtJjssW9eKF-pUIsS8iNt5Z0QOjICtnwmhQ66xccJO61mi3EEdq_A1">`

Then we can POST to https://www.applebees.com/api/sitecore/Locations/LocationSearchAsync with a body like: 

```
ResultsPage: /locations/results
LocationRoot: {3B216C7F-CB81-4126-A2CE-33AD79B379CF}
NumberOfResults: 10
LoadResultsForCareers: False
MaxDistance: 5000
UserLatitude:
UserLongitude:
SearchQuery: NC
__RequestVerificationToken: 1pnS6KstxW837iZ1d2mBXThK2NdR7CdUvPhacRii30k4sYM2oucfrc5iOl7mwUTgvY-rvS_P9uUflRGtHrhLy2pJxSxuta8d0Zjjp6ajaRg1
```

The actual website defaults NumberOfResults to 10 and the SearchQuery to a city and state, but I was able to set the NumberOfResults to 1000 and the SearchQuery to just a state abbreviation. 



Here’s a snippet of how the API responses are formatted: 


```
{
   "Locations":[
      {
         "Location":{
            "Id":"42a85dbd-b049-48e1-a81d-f4d2d3f6f3c5",
            "ExternalId":"21961",
            "StoreNumber":"9243",
            "BridgId":"",
            "SupportsOnlineOrdering":true,
            "Name":"E. SIX FORKS",
            "Street":"501 E. Six Forks Road ",
            "City":"Raleigh",
            "State":"NC",
            "Country":"US",
            "Zip":"27609",
            "PhoneNumber":null,
            "WebsiteUrl":"/en/restaurants-raleigh-nc/501-e-six-forks-road-9243",
            "ParentCompany":"APPLEBEE\u0027S RESTAURANTS MID-ATLANTIC GROUP (COMPANY OWNED)",
            "ClickToHire":"https://recruiting.talentreef.com/applebees-services-inc",
            "Coordinates":{
               "Latitude":35.820001,
               "Longitude":-78.62325,
               "Cacheable":false,
               "Immutable":true
            },
            "Amenities":[
               {
                  "ID":"00000000-0000-0000-0000-000000000000",
                  "ItemName":null,
                  "Name":"Carside To Go",
                  "Icon":null,
                  "SortOrder":1,
                  "AmenitySource":"00000000-0000-0000-0000-000000000000",
                  "SourceFieldName":null,
                  "AltText":null,
                  "Summary":null,
                  "IsManual":false,
                  "IsAvailable":true,
                  "Spid":"15"
               },
               {
                  "ID":"00000000-0000-0000-0000-000000000000",
                  "ItemName":null,
                  "Name":"Pick Up Inside",
                  "Icon":null,
                  "SortOrder":2,
                  "AmenitySource":"00000000-0000-0000-0000-000000000000",
                  "SourceFieldName":null,
                  "AltText":null,
                  "Summary":null,
                  "IsManual":false,
                  "IsAvailable":true,
                  "Spid":"29"
               },
               {
                  "ID":"00000000-0000-0000-0000-000000000000",
                  "ItemName":null,
                  "Name":"Delivery",
                  "Icon":null,
                  "SortOrder":3,
                  "AmenitySource":"00000000-0000-0000-0000-000000000000",
                  "SourceFieldName":null,
                  "AltText":null,
                  "Summary":null,
                  "IsManual":false,
                  "IsAvailable":true,
                  "Spid":"21"
               },
               {
                  "ID":"00000000-0000-0000-0000-000000000000",
                  "ItemName":null,
                  "Name":"Wi-Fi Available",
                  "Icon":null,
                  "SortOrder":5,
                  "AmenitySource":"00000000-0000-0000-0000-000000000000",
                  "SourceFieldName":null,
                  "AltText":null,
                  "Summary":null,
                  "IsManual":false,
                  "IsAvailable":true,
                  "Spid":"27"
               }
            ],
            "HasCatering":false,
            "AddressString":"501 E. Six Forks Road  Raleigh; NC US 27609",
            "MenuData":null,
            "CustomerFacingMessage":null,
            "DeliveryProviders":null
         },
         "Contact":{
            "PhoneNumberFormat":"000-000-0000",
            "Phone":"(919) 856-9030"
         },
         "HoursOfOperation":{
            "DaysOfOperation":[
               {
                  "DayofWeek":"Sunday",
                  "OpenHours":"11:30 AM",
                  "CloseHours":"9:00 PM",
                  "Is24Hours":false
               },
               {
                  "DayofWeek":"Monday",
                  "OpenHours":"11:30 AM",
                  "CloseHours":"9:00 PM",
                  "Is24Hours":false
               },
               {
                  "DayofWeek":"Tuesday",
                  "OpenHours":"11:30 AM",
                  "CloseHours":"9:00 PM",
                  "Is24Hours":false
               },
               {
                  "DayofWeek":"Wednesday",
                  "OpenHours":"11:30 AM",
                  "CloseHours":"9:00 PM",
                  "Is24Hours":false
               },
               {
                  "DayofWeek":"Thursday",
                  "OpenHours":"11:30 AM",
                  "CloseHours":"9:00 PM",
                  "Is24Hours":false
               },
               {
                  "DayofWeek":"Friday",
                  "OpenHours":"11:30 AM",
                  "CloseHours":"10:00 PM",
                  "Is24Hours":false
               },
               {
                  "DayofWeek":"Saturday",
                  "OpenHours":"11:30 AM",
                  "CloseHours":"10:00 PM",
                  "Is24Hours":false
               }
            ],
            "DaysOfOperationVM":[
               {
                  "LocationHourLabel":"Sunday",
                  "LocationHourText":"11:30 AM - 9:00 PM"
               },
               {
                  "LocationHourLabel":"Monday",
                  "LocationHourText":"11:30 AM - 9:00 PM"
               },
               {
                  "LocationHourLabel":"Tuesday",
                  "LocationHourText":"11:30 AM - 9:00 PM"
               },
               {
                  "LocationHourLabel":"Wednesday",
                  "LocationHourText":"11:30 AM - 9:00 PM"
               },
               {
                  "LocationHourLabel":"Thursday",
                  "LocationHourText":"11:30 AM - 9:00 PM"
               },
               {
                  "LocationHourLabel":"Friday",
                  "LocationHourText":"11:30 AM - 10:00 PM"
               },
               {
                  "LocationHourLabel":"Saturday",
                  "LocationHourText":"11:30 AM - 10:00 PM"
               }
            ],
            "All24Hrs":false
         },
         "Operation":{
            "UtcOffset":null,
            "TodayOpen":"11:30 AM",
            "TodayClose":"9:00 PM",
            "NextOpen":"11:30",
            "TodaysOperationText":"Today\u0027s Hours: 11:30 AM-9:00 PM",
            "IsToday24Hours":false
         },
         "Distance":22.605851404707163,
         "MyLocation":true,
         "DirectionLink":"https://www.google.com/maps/dir//501%20E.%20Six%20Forks%20Road%20%20Raleigh%20NC%20US%2027609",
         "MenuLink":null,
         "NearestRank":0,
         "Disclaimers":null,
         "UTCOffset":null,
         "CanChangeLocations":true
      },
      ...
```