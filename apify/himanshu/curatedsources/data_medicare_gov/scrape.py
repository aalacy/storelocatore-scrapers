import csv
import sys
import requests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('data_medicare_gov')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["Facility_ID","locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses =[]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://data.medicare.gov/Hospital-Compare/Hospital-General-Information/xubh-q36u/data"
    return_main_object=[]
    location_url = "https://data.medicare.gov/api/id/xubh-q36u.json?$query=select%20*%2C%20%3Aid%20limit%205344"
    # location_url = "https://data.medicare.gov/api/id/xubh-q36u.json?$query=select%20*%2C%20%3Aid%20limit%205344"
    locs = requests.get(location_url, headers=headers).json()
    for loc in locs:
       
        tem_var =[]
        Facility_ID = loc['provider_id']
        location_name = loc['hospital_name']
        # logger.info(location_name)
        street_address = loc['address']
        city = loc['city']
        state = loc['state']
        zipp = loc['zip_code']
        if len(zipp)==5:
            country_code = "US"
    

        store_number = "<MISSING>"
        phone = loc['phone_number']
        location_type = loc['hospital_type']
        
        if "geocoded_column" in loc:
            # logger.info(loc['geocoded_column']['coordinates'][0])
            latitude = loc['geocoded_column']['coordinates'][1]
            longitude = loc['geocoded_column']['coordinates'][0]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"
        tem_var.append(Facility_ID)
        tem_var.append("https://data.medicare.gov/Hospital-Compare/Hospital-General-Information/xubh-q36u/data")
        tem_var.append(location_name)
        tem_var.append(street_address.capitalize())
        tem_var.append(city.capitalize())
        tem_var.append(state)
        tem_var.append(zipp)
        tem_var.append(country_code)
        tem_var.append(store_number)
        tem_var.append(phone)
        tem_var.append(location_type)
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(hours_of_operation)
        tem_var.append(page_url)
        
        if tem_var[2] in addresses:
            continue
        addresses.append(tem_var[2])
        # logger.info(tem_var)
        # return_main_object.append(tem_var)
        yield tem_var
        
    # return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
