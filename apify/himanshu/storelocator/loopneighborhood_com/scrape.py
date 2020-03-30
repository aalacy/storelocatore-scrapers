import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://www.loopneighborhood.com"
    header = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Host': "www.loopneighborhood.com"
        }
    r = session.get(base_url+ "/locations",headers= header)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"results_entry"}):
        name = location.find("div",{"class":"results_location_title"}).text.strip()
        street = location.find("p",{"class":"slp_result_address slp_result_street"}).text.strip()
        address_details = location.find("p",{"class":"slp_result_address slp_result_citystatezip"}).text.strip().split(",")
        geo_location = location.find("a",{"class":'storelocatorlink'})['href']
        store=[]
        store.append("http://www.loopneighborhood.com")
        store.append(name)
        store.append(street)
        store.append(address_details[0] if address_details[0] != "" else "<MISSING>")
        store.append(address_details[1].split(" ")[-2])
        store.append(address_details[1].split(" ")[-1])
        store.append("US")
        store.append(location["id"].split(" ")[-1])
        store.append(location.find("span",{"class":"slp_result_address slp_result_phone"}).text.strip())
        store.append("loop Convenience Store")
        store.append(geo_location.split("/")[-1].split(",")[0])
        store.append(geo_location.split("/")[-1].split(",")[1])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
