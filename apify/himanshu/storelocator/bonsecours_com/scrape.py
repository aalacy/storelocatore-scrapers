import csv
import requests
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
import sgzip
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bonsecours_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess = []
    addressess123 =[]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    returnres=[]
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        r = session.get("https://www.bonsecours.com/bonsecours/api/v1/locations?Latitude="+ str(lat) +"&Longitude=" + str(lng),headers=headers).json()
        for link  in r['Results']:
            location_type = link['Location']['FacilityType']['SchemaPlaceType']
            page_url = "https://www.bonsecours.com"+link['Location']['DetailsLink']
            location_name = link['Location']['Name']
            street_address = link['Location']['Address']['StreetDisplay']
            city = link['Location']['Address']['City']
            state =link['Location']['Address']['StateAbbr']
            zipp  =link['Location']['Address']['PostalCode']
            country_code = "US"
            store_number="<MISSING>"
            r1 = session.get(page_url,headers=headers)
            soup_loc = BeautifulSoup(r1.text,"lxml")
            phone = link['Location']['Phone']
            # logger.info(page_url)
            try:
                hours_of_operation =" ".join(list(soup_loc.find("div",class_="col w-100 w-sm-50 w-md-100 w-xl-50 py3 small bl").stripped_strings))
            except:
                hours_of_operation="<MISSING>"
            # logger.info(hours_of_operation)
            longitude = link['Location']['Latitude']
            latitude = link['Location']['Longitude']
            store =[]
            street_address =street_address.split("Floor")[0].split("Suite")[0].replace(",",'').replace(state,'')
            if street_address.strip()[0]=='0':
                street_address = street_address.strip()[1:]
            store = ["https://www.bonsecours.com/", location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            if str(store[2]+store[-5])  in addressess123:
                continue
            addressess123.append(str(store[2]+store[-5]))
            yield store
            #logger.info(store)
            
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
    # return returnres;

def scrape():
    data = fetch_data();
    write_output(data)
scrape()
