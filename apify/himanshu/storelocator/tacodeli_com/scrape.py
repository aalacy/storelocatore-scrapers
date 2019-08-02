import csv
import requests
from bs4 import BeautifulSoup
import re
import json

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

    base_url = "https://www.tacodeli.com"
    r = requests.get("https://www.tacodeli.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "locationsJson" in script.text:
            location_list = json.loads(script.text.split("locationsJson=")[1].split("]}")[0])
            for i in range(len(location_list)):
                store_data = location_list[i]
                store = []
                store.append("https://www.tacodeli.com")
                store.append(store_data["title"])
                store.append(store_data["address"])
                store.append(store_data["city"])
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("US")
                store.append(store_data["id"])
                store.append(store_data["phone"])
                store.append("tacodeli")
                store.append(store_data["lat"])
                store.append(store_data["lng"])
                location_request = requests.get(store_data["link"],headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                store_hours = location_soup.find_all("div",{"class":"weekdays"})
                hours = ""
                for k in range(len(store_hours)):
                    hours = hours + " ".join(list(store_hours[k].stripped_strings)) + " "
                store.append(hours if hours != "" else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
