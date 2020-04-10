import csv
from bs4 import BeautifulSoup
import re
import json
import requests
 

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    
    headers = {
    'accept': "application/json, text/javascript, */*; q=0.01",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-US,en;q=0.9",
    'connection': "keep-alive",
    'content-type': "application/json; charset=utf-8",
    'host': "www.piedmont.org",
    'referer': "https://www.piedmont.org/locations/locations-map",
    'sec-fetch-dest': "empty",
    'sec-fetch-mode': "cors",
    'sec-fetch-site': "same-origin",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    'x-requested-with': "XMLHttpRequest",
    'cache-control': "no-cache",
    'postman-token': "b8d9f318-2038-6a3f-6b5d-c70ac7ec0ea7"
    }
    result_coords = []
    url = "https://www.piedmont.org/_services/LocationsService.asmx/GetLocations"

    try:
        response = requests.request("GET", url, headers=headers)
    except:
        pass
    json_data = response.json()
    for i in json_data['d']:
        if i['OfficeHours'] != None:
            hours_of_operation =i['OfficeHours']
        else:
            hours_of_operation = "<MISSING>"
        if hours_of_operation:
            hours_of_operation=hours_of_operation
        else:
            hours_of_operation = "<MISSING>"



        street_address = i["Address1"].split("suite")[0].split("floor")[0]
        page_url = i["PracticeID"]
        city = i["City"]
        state = i["State"]
        zipp = i["Zip"]
        phone = i["Phone"]
        latitude = i["Latitude"]
        longitude = i["Longitude"]
        loctype = i['ParentPractice']['LocationTitle']
        store_number = "<MISSING>"
        store = []
        store.append(url)
        store.append(i['Name']) 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation)
        store.append("https://www.piedmont.org/locations/location-details?practice="+str(page_url))

        if store[2] in addresses:
            continue
        addresses.append(store[2])
        # print("data ==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store
                
       
                  
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
