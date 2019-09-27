import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "http://daysinn.ca"
    r = requests.get('https://www.wyndhamhotels.com/en-ca/days-inn/locations', headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("ul", {"class": "property-list"}):
        for semi_parts in parts.find_all("li", {"class": "property"}):
            return_object = []
            store_request = requests.get('https://www.wyndhamhotels.com' + semi_parts.find("a")['href'])
            
            store_soup = BeautifulSoup(store_request.text, "lxml")
           
            if (store_soup.find("div", {"class": "property-info"})):
                locationDetails = store_soup.find("div", {"class": "property-info"})
                temp_storeaddresss = list(locationDetails.stripped_strings)
                location_name = temp_storeaddresss[0]
                street_address = temp_storeaddresss[1]
                city = temp_storeaddresss[3]
                if(len(temp_storeaddresss) == 9):
                    state = temp_storeaddresss[5]
                    store_zip = temp_storeaddresss[6]
                    country = temp_storeaddresss[7]
                    phone = temp_storeaddresss[8]
                elif(len(temp_storeaddresss) == 8):
                    store_zip = temp_storeaddresss[5]
                    state = temp_storeaddresss[6]
                    country = "US"
                    phone = temp_storeaddresss[7]
                else:
                    store_zip = '<MISSING>'
                    phone = temp_storeaddresss[6]
                    state = temp_storeaddresss[5]
                    country = "US"
                return_object.append(base_url)
                return_object.append(location_name)
                return_object.append(street_address)
                return_object.append(city)
                return_object.append(state)
                return_object.append(store_zip)
                return_object.append(country)
                return_object.append("<MISSING>")
                return_object.append(phone)
                return_object.append("daysinn")
                return_object.append("<MISSING>")
                return_object.append("<MISSING>")
                return_object.append("<MISSING>")
                return_main_object.append(return_object)
                print(return_main_object)

    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


