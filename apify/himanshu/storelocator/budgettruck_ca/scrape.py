import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8",newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess = []

    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.budgettruck.ca/"

    states = session.get("https://www.budgettruck.ca/en/bin/location-browse.html/ca.json").json()
    for region in states:
        city_list = session.get("https://www.budgettruck.ca/en/bin/location-browse.html/"+str(region['relPath'])+".json").json()
    
        for city_name in city_list:
            
            payload = "{\"country\":\"CA\",\"state\":\""+str(region['code'].upper())+"\",\"city\":\""+str(city_name['name'])+"\",\"rqHeader\":{\"locale\":\"en_US\",\"domain\":\"ca\"}}"
            headers = {
                'content-type': "application/json",
                'cache-control': "no-cache",

                }
            try:
                json_data = session.post("https://www.budgettruck.ca/webapi/station/lat-long", data=payload, headers=headers).json()['stationInfoList']
            except:
                continue
           
            for dealer in json_data:
                locator_domain = base_url
                location_name = dealer['description']
                street_address = dealer['address1']
                city = dealer['city']
                state = dealer['stateCode']
                zipp = dealer['zipCode']
                country_code = dealer['countyCode']
                phone = dealer['phoneNumber']
                location_type = dealer['licInd']
                try:
                    latitude = dealer['latitude']
                    longitude = dealer['longitude']
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                hours_of_operation = dealer['hoursOfOperation']
                page_url = "https://www.budgettruck.ca/en/locations/"+dealer['augmentDataMap']['REL_PATH']

                
                store = []
                store.append(locator_domain)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append(country_code)
                store.append('<MISSING>')
                store.append(phone)
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(page_url)
            

                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                yield store
           



def scrape():
    data = fetch_data()
    write_output(data)
scrape()
