import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import ast
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://www.abcwarehouse.com"
    r = session.get(base_url + "/store-locator",verify=False)

    soup = BeautifulSoup(r.text,"lxml")
    store_list = ast.literal_eval(soup.find("input",{"class": "shop-resources"})["data-markersdata"])
    return_main_object = []
    for i in range(len(store_list)):
        store_object = store_list[i]
        store_address = list(BeautifulSoup(store_object["ShortDescription"],"lxml").stripped_strings)
        store = []
        store.append("https://www.abcwarehouse.com")
        store.append(store_object["Name"])
        store.append(store_address[0])
        if len(store_address) == 4:
            store.append(store_address[1])
            if "," in store_address[2]:
                store.append(store_address[2].split(",")[1].split(" ")[1])
                store.append(store_address[2].split(",")[1].split(" ")[2])
            else:
                store.append(store_address[2].split(" ")[0])
                store.append(store_address[2].split(" ")[1])
        else:
            store.append(store_address[1].split(",")[0])
            store.append(store_address[1].split(",")[1].split(" ")[1])
            store.append(store_address[1].split(",")[1].split(" ")[2])
        store.append("US")  
        store.append(store_object["Id"])
        store.append(store_address[-1])
        store.append("<MISSING>")
        store.append(store_object["Latitude"])
        store.append(store_object["Longitude"])
        store.append("<MISSING>")
        data = store_object["Name"].lower().replace(" ","-")
        page_url = ("https://www.abcwarehouse.com/"+str(data)+"-5").replace('roseville-5',"roseville").replace("mt.-pleasant-5","mt-pleasant-5").replace("sylvania-5","sylvania-6").replace("alpine-5","alpine-6").replace("rochester-hills-5","rochester-hills")
        store.append(page_url)
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
