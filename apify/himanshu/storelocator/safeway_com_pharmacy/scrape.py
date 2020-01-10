import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from datetime import datetime

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

   
    base_url= "https://www.safeway.com/pharmacy.html"

    
    headers = {   
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',        
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'accept': 'application/json'
    }
    while zip_code:
        result_coords = []

        location_url = "https://local.safeway.com/search.html?q="+str(zip_code)+"&storetype=5657&l=en"
        
        r = requests.get(location_url, headers=headers).json()
        current_results_len = len(r['response']['entities'])

        for i in r['response']['entities']:
            city = i['profile']['address']['city']
            street_address = i['profile']['address']['line1']
            state = i['profile']['address']['region']
            zipp = i['profile']['address']['postalCode']
            location_type = i['profile']['c_type']
            phone = i['profile']['mainPhone']['display']
            country_code = i['profile']['mainPhone']['countryCode']  
            latitude = i['profile']['yextDisplayCoordinate']['lat']
            longitude = i['profile']['yextDisplayCoordinate']['long']	
            page_url = i['profile']['websiteUrl']

            drive_hours = ''
            for drive in  i['profile']['hours']['normalHours']: 
            
                    
                if drive['isClosed'] == False:
                    for interval in (drive['intervals']):
                        if interval['start'] == 0:
                            value_starttime = datetime.strptime(str(interval['start']), "%H")
                            starttime= value_starttime.strftime("%I:%M %p")
                        else:
                            value_starttime = datetime.strptime(str(interval['start']), "%H%M")
                            starttime= value_starttime.strftime("%I:%M %p")
                        if interval['end'] == 0:
                            value_endtime = datetime.strptime(str(interval['end']), "%H")
                            endtime= value_endtime.strftime("%I:%M %p")
                        else:
                            value_endtime = datetime.strptime(str(interval['end']), "%H%M")
                            endtime= value_endtime.strftime("%I:%M %p")
                        drive_hours = drive_hours+" "+drive['day']+" "+str(starttime)+"-"+str(endtime)
                else:
                    drive_hours = drive_hours+" "+drive['day']+" "+"closed"
            hours_of_operation = drive_hours

            r2 = requests.get(page_url, headers=headers)
            soup2 = BeautifulSoup(r2.text, "lxml")
            location_name = soup2.find("h1",{"class":"ContentBanner-h1"}).text
            
        
            result_coords.append((latitude, longitude))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone )
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            #print("data =="+str(store))
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
        
        
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
