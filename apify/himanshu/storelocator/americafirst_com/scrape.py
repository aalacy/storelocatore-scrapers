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
    base_url = "https://www.americafirst.com"
    r = session.get(base_url + "/content/afcu/en/about/branch-search-results/_jcr_content/main/branch_search_result.nocache.html")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []

    for li in soup.find_all("li",{"class": "card"}):
        store_url = li.find("div",{"class":"text-center button"}).find('a')["data-href"]
        store_request = session.get(base_url + store_url)
        store_soup = BeautifulSoup(store_request.text,"lxml")
        name = list(store_soup.find("h1",{"class":'text-center'}).stripped_strings)[0]
        store_details = list(store_soup.find("div",{"class": "col-lg-6"}).stripped_strings)
        store_address = []
        for i in range(len(store_details)):
            if store_details[i] == "Address":
                for k in range(i+1,len(store_details)):
                    if store_details[k] != "Driving Directions":
                        store_address.append(store_details[k])
                    else:
                        break
                break
        open_hours = []
        for i in range(len(store_details)):
            if store_details[i] == "Lobby Hours":
                for k in range(i+1,len(store_details)):
                    if store_details[k] != "Drive-up Hours":
                        open_hours.append(store_details[k])
                    else:
                        break
                break
        store = []
        store.append("https://www.americafirst.com")
        store.append(name)
        store.append(store_address[0])
        store.append(store_address[1].split(",")[0])
        store.append(store_address[1].split(",")[1].split(" ")[1])
        store.append(store_address[1].split(",")[1].split(" ")[2])
        store.append("US")
        store.append(store_url.split("siteNo=")[1].split("&")[0])
        store.append("<MISSING>")
        store.append("America first credit union")
        store.append(store_url.split("lat=")[1].split("&")[0])
        store.append(store_url.split("lng=")[1])
        store.append(" ".join(open_hours))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
