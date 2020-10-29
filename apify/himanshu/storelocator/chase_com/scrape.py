import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
import time
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chase_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline= "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    base_url= "https://chase.com/"

    
    headers = {   
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',        
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'accept': 'application/json'
    }
    offset = []
    for data in range(553):
        
        # logger.info(data)
        offset.append(data*10)
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~"+str(offset[data]))
        location_url = "https://locator.chase.com/search?offset="+str(offset[data])
        # logger.info(location_url)
    
        r = session.get(location_url, headers=headers).json()
        for i in r['response']['entities']:
            city = i['profile']['address']['city']
            street_address = i['profile']['address']['line1']
            state = i['profile']['address']['region']
            zipp = i['profile']['address']['postalCode']
            location_type = i['profile']['c_bankLocationType']
            if "c_geomodifier" in i['profile']:
                location_name = i['profile']['c_geomodifier']
            else:
                location_name = "<MISSING>"
            phone = i['profile']['mainPhone']['display']
            country_code = i['profile']['mainPhone']['countryCode']
            if "displayCoordinate" in i['profile']:
                latitude = i['profile']['displayCoordinate']['lat']
                longitude = i['profile']['displayCoordinate']['long']
            else:
                latitude = i['profile']['yextDisplayCoordinate']['lat']
                longitude = i['profile']['yextDisplayCoordinate']['long']

            page_url = i['profile']['c_pagesURL']
            

            if location_type == "Branch":
                store_number = i['profile']['c_rawEntityId']
                drive_hours = 'Drive-up Hours :'  
                lobby_hours = 'Lobby :'
                if "c_driveupHours" in  i['profile']:
                    for drive in  i['profile']['c_driveupHours']['normalHours']: 
                        
                        if drive['isClosed'] == False:
                            for interval in (drive['intervals']):
                                value_starttime = datetime.strptime(str(interval['start']), "%H%M")
                                starttime= value_starttime.strftime("%I:%M %p")
                                value_endtime = datetime.strptime(str(interval['end']), "%H%M")
                                endtime= value_endtime.strftime("%I:%M %p")
                                drive_hours = drive_hours+" "+drive['day']+" "+str(starttime)+"-"+str(endtime)
                        else:
                            drive_hours = drive_hours+" "+drive['day']+" "+"closed"

                    for lobby in  i['profile']['c_lobbyHours']['normalHours']: 
                        
                        if lobby['isClosed'] == False:
                            for interval in (lobby['intervals']):
                                value_starttime = datetime.strptime(str(interval['start']), "%H%M")
                                starttime= value_starttime.strftime("%I:%M %p")
                                value_endtime = datetime.strptime(str(interval['end']), "%H%M")
                                endtime= value_endtime.strftime("%I:%M %p")
                                lobby_hours = lobby_hours+" "+lobby['day']+" "+str(starttime)+"-"+str(endtime)
                        else:
                            lobby_hours = lobby_hours+" "+lobby['day']+" "+"closed"

                    hours_of_operation = lobby_hours+" "+drive_hours
        
                else:
                    store_number = "<MISSING>"
                    hours_of_operation = "Open 24 Hours"
                try:
                    operating_info_tag = i['profile']['c_emergencyMessage'].split(".")[0].strip()
                    if "Temporarily Closed" in operating_info_tag:
                        operating_info = operating_info_tag
                    else:
                        operating_info = "<MISSING>"
                except:
                    operating_info = "<MISSING>"
                store = []
                # result_coords.append((latitude, longitude))
                store.append(base_url)
                store.append(location_name)
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # logger.info("data =="+str(store))
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                yield store

       

            
            
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
