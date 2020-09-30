import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://www.americangirl.com"
    r = session.get(base_url + "/retail/charlotte")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for a in soup.find_all("a",{"class": "select-location"}):
        if a['href'][0] != "/":
            break
        page_url = base_url + a['href']
        location_request = session.get(page_url)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        try:
            store_data = json.loads(location_soup.find("div",{"class": "map-module"})["data-coordinate"])[0]
            hours = list(location_soup.find("div",{"id":"collapseListGroup1"}).stripped_strings)
            name = list(location_soup.find("span",{"class": "pull-left"}).stripped_strings)[0]
            store = []
            store.append("https://www.americangirl.com")
            store.append(name)
            if len(store_data["locationName"].split(",")) == 2 and "New York" in store_data["locationName"]:
                store.append(store_data["locationName"].split("New York")[0])
                store.append("New York")
                store.append(store_data["locationName"].split(",")[-1].split(" ")[1])
                store.append(store_data["locationName"].split(",")[-1].split(" ")[-1])
            else:
                store.append(store_data["locationName"].split(",")[-3])
                store.append(store_data["locationName"].split(",")[-2])
                store.append(store_data["locationName"].split(",")[-1].split(" ")[1])
                store.append(store_data["locationName"].split(",")[-1].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            phone = "877-247-5223"
            store.append(phone)
            store.append("americangirl")
            store.append(store_data["lattitude"])
            store.append(store_data["longitude"])
            store.append(" ".join(hours))
            store.append(page_url)
            store = [x.replace("—","-") if type(x) == str else x for x in store] 
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            return_main_object.append(store)
        except Exception as e:
            pass
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()