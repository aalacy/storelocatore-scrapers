import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://wingspizzanthings.com/"
    r = requests.get("http://wingspizzanthings.com/locations.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("map",{'id':"map1"}).find_all("area",{"href":re.compile(".")})[:-1]:
        location_request = requests.get(base_url + location['href'],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        for store in location_soup.find("div",{'id':"divMain"}).find_all("div",recursive=False):
            if len(store.find_all("p",{"class":"Address"})) > 1:
                location_details = list(store.stripped_strings)
                if len(location_details[3].split(",")) == 1:
                    location_details.insert(1,"")
                store = []
                store.append("http://wingspizzanthings.com")
                store.append(" ".join(location_details[0:2]))
                store.append(location_details[2])
                store.append(location_details[3].split(",")[0])
                store.append(location_details[3].split(",")[1].split(" ")[-2])
                store.append(location_details[3].split(",")[1].split(" ")[-1])
                store.append("US")
                store.append("<MISSING>")
                store.append(" ".join(location_details[4:7]).replace("Phone: ","").replace("FOOD ","").split("Fax")[0] if len(location_details) > 5 else " ".join(location_details[4:6]).replace("Phone: ","").replace("FOOD ","").split("Fax")[0])
                store.append("wings pizza n things")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
