import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
            'accept': "application/json;v=1",
            'content-type': "application/json",
            'host': "api.capitalone.com",
            'origin': "https://locations.capitalone.com",
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            'cache-control': "no-cache",
    }
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=["US"])
    MAX_RESULTS = 150
    MAX_DISTANCE = 50
    coord = search.next_coord()
    while coord:
        result_coords = []
        
       
        payload = "{\"variables\":{\"input\":{\"lat\":"+str(coord[0])+",\"long\":"+str(coord[1])+",\"radius\":50,\"locTypes\":[\"cafe\",\"branch\"],\"servicesFilter\":[]}},\"query\":\"\\n query geoSearch($input: GeoSearchInput!){\\n geoSearch(input: $input){\\n locType\\n locationName\\n locationId\\n address {\\n addressLine1\\n stateCode\\n postalCode\\n city\\n }\\n services\\n distance\\n latitude\\n longitude\\n slug\\n seoType\\n ... on Atm {\\n open24Hours\\n }\\n\\t ... on Branch {\\n phoneNumber\\n timezone\\n lobbyHours {\\n day\\n open\\n close\\n }\\n driveUpHours {\\n day\\n open\\n close\\n }\\n temporaryMessage\\n\\t }\\n\\t ... on Cafe {\\n phoneNumber\\n photo\\n timezone\\n hours {\\n day\\n open\\n close\\n }\\n temporaryMessage\\n }\\n }\\n }\"}"
       
        json_data = session.post("https://api.capitalone.com/locations",headers=headers,data=payload).json()['data']['geoSearch']
        
        for store_data in json_data:
            lat = store_data["latitude"]
            lng = store_data["longitude"]
            result_coords.append((lat, lng))
            store = []
            store.append("https://www.capitalone.com")
            store.append(store_data["locationName"])

            # if "Temporarily Closed" in store[-1]:
            #     continue

            store.append(store_data["address"]["addressLine1"])
            if store[-1].lower() in addresses:
                continue
            addresses.append(store[-1].lower())
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["stateCode"])
            store.append(store_data["address"]["postalCode"])
            store.append("US")
            store.append(store_data["locationId"])
            store.append(store_data["phoneNumber"] if "phoneNumber" in store_data and store_data["phoneNumber"] != "" and store_data["phoneNumber"] != None  else "<MISSING>")
            store.append(store_data["locType"])
            store.append(lat)
            store.append(lng)
            hours = ""
            cafe_hours = ""
            lobbyHours = "Lobby Hours : "
            driveUpHours = "Drive Hours : "
            if "hours" in store_data:
                for day in store_data['hours']:
                    if day['open'] == "Closed" or day['close'] == "Closed":
                        cafe_hours += " " + day['day'] + " Closed "
                    else:
                        cafe_hours += " " + day['day'] + " " + day['open'] +" - " + day['close'] + " "
                hours += cafe_hours
            if "lobbyHours" in store_data:
                for day in store_data['lobbyHours']:
                    if day['open'] == "Closed" or day['close'] == "Closed":
                        lobbyHours += " " + day['day'] + " Closed "
                    else:
                        lobbyHours += " " + day['day'] + " " + day['open'] +" - " + day['close'] + " "
                hours += " " + lobbyHours
            if "driveUpHours" in store_data:
                for day in store_data['driveUpHours']:
                    if day['open'] == "Closed" or day['close'] == "Closed":
                        driveUpHours += " " + day['day'] + " Closed "
                    else:
                        driveUpHours += " " + day['day'] + " " + day['open'] +" - " + day['close'] + " "
                hours += " " + driveUpHours
            store.append(hours.strip() if hours != "" else "<MISSING>")
            
            store.append("https://locations.capitalone.com/bank/"+str(store_data["address"]["stateCode"].lower())+"/"+str(store_data['slug']))
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store
        
        if len(json_data) < MAX_RESULTS:
           
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
           
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
