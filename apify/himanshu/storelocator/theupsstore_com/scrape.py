import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast
​
​
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
​
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
​
​
def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    return_object = []
    base_url = "https://www.theupsstore.com"
    r = requests.get(base_url + '/about/new-locations', headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("div", {"id": "ctl01_FWTxtContentDetailOne_ctl00"}):
        for semi_part in parts.find_all("p")[1:]:
            if not (semi_part.find_all("strong")):
                string = list(semi_part.stripped_strings)
               # print(string)
            else:
                string = list(semi_part.stripped_strings)
                del string[0]
             #   print(string)
           # print(string)
            location_name = string[0]
            street_address = string[1]
            city = string[2].split(",")[0]
            state_zip = string[2].split(",")[1]
            state = state_zip.split(" ")[1]
            store_zip = state_zip.split(" ")[2]
            if(len(string[0].split("#")) == 2):
                store_number = string[0].split("#")[1]
            else:
                store_number= "<MISSING>"
            return_object.append(base_url)
            return_object.append(location_name)
            return_object.append(street_address)
            return_object.append(city)
            return_object.append(state)
            return_object.append(store_zip)
            return_object.append("US")
            return_object.append(store_number)
            return_object.append("<MISSING>")
            return_object.append("The Ups Store")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_main_object.append(return_object)
        return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
​
​
scrape()
