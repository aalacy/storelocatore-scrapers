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
def return_header(host):
    return {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': host,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    
def fetch_data():
    data="action=call_endpoint_api"
    r = session.post("https://ontario.foodland.ca/wp-admin/admin-ajax.php",data=data,headers=return_header('foodland.ca'))
    data = r.json()["data"]["stores"]
    return_main_object = []
    for key in data:
        states = data[key]
        for locations in states:
            location = states[locations]
            for store in location:
                location_url = location[store]
                location_header = location_url.split("https://")[1].split("/")[0]
                location_request = session.get(location_url,headers=return_header(location_header))
                location_soup = BeautifulSoup(location_request.text,"lxml")
                name = location_soup.find("div",{"class": "store-info"}).find("h2").text
                store_details = list(location_soup.find("div",{"class":"store-info"}).stripped_strings)
                store = []
                store.append("https://www.foodland.ca")
                store.append(name)
                if len(store_details) < 7 and "Store Manager" in " ".join(store_details):
                    store.append("<MISSING>")
                    store.append(store_details[1].split(",")[0])
                    store.append(store_details[1].split(",")[1].split(".")[0])
                    store.append(store_details[1].split(",")[1].split(".")[1].strip())
                    store.append("CA")
                    store.append(location_url.split("?snumber=")[1])
                    store.append(store_details[2].split("Tel:")[1].strip())
                    store.append("food loand")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                else:
                    store.append(store_details[1])
                    store.append(store_details[2].split(",")[0])
                    store.append(store_details[2].split(",")[1].split(".")[0])
                    store.append(store_details[2].split(",")[1].split(".")[1].strip())
                    store.append("CA")
                    store.append(location_url.split("?snumber=")[1])
                    store.append(store_details[3].split("Tel:")[1].strip())
                    store.append("food loand")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                hours = list(location_soup.find("div",{"class": "location-details clearfix"}).find("p").stripped_strings)
                if hours == []:
                    hours = "<MISSING>"
                store.append(" ".join(hours))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
