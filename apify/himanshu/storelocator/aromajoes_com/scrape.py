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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://aromajoes.com"
    link = "https://aromajoes.com/locations/"
    r = session.get(link,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if 'var json_markers = ' in script.text:
            location_list = json.loads(script.text.split('var json_markers = ')[1].split("}];")[0] + "}]")
            for i in range(len(location_list)):
                store_data = location_list[i]
                if "coming soon" in store_data["content"].lower():
                    continue
                hours = BeautifulSoup(store_data["content"],"lxml").text.replace("\xa0"," ").replace("\n"," ").replace("–","-").replace("NOW OPEN","").replace("!","").strip()
                if "CLOSED EASTER" in hours:
                    hours = hours[:hours.find("CLOSED")].strip()
                if "Cafe" in hours:
                    hours = hours[:hours.find("Cafe")].strip()
                store = []
                store.append("https://aromajoes.com")
                store.append(link)
                store.append(store_data["title"])
                store.append(store_data["address"].split("-")[1].strip())
                store.append(store_data["address"].split("-")[0].split(",")[0].strip())
                
                state = store_data["state_code"].strip()
                zip_code = store_data["zip_code"].strip()
                if zip_code == "09152":
                    zip_code = "01952"
                if zip_code == "03801" and state == "ME":
                    zip_code = "33069"
                    state = "FL"
                if zip_code == "03893":
                    zip_code = "03839"
                    
                store.append(state)
                store.append(zip_code)
                store.append("US")
                store.append(store_data["store_no"].strip())
                store.append(store_data["phone"].strip() if store_data["phone"] != "Comin' Soon!" else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_data['latitude'].strip())
                store.append(store_data['longitute'].strip())
                store.append(hours if hours != "" else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
