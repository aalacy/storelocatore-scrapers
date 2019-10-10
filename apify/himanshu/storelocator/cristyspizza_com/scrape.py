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
    base_url = "https://cristyspizza.com"
    r = requests.get("https://cristyspizza.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    hours_object = {}
    for location in soup.find_all("div",{'class':"fl-html"}):
        if location.find("p") == None:
            continue
        phone = list(location.find("strong").stripped_strings)[0].replace("(","").replace(")","").replace(" ","-")
        hours = ''
        for p_tag in location.find_all("p")[2:-1]:
            hours = hours + " "  + " ".join(list(p_tag.stripped_strings))
        hours_object[phone] = hours
    for script in soup.find_all("script"):
        if '.maps(' in script.text:
            location_list = json.loads(script.text.split('.maps(')[1].split("}})")[0] + "}}")['places']
            for store_data in location_list:
                store = []
                store.append("https://cristyspizza.com")
                store.append(store_data['title'])
                store.append(store_data["address"])
                store.append(store_data["location"]['city'])
                store.append(store_data["location"]['state'])
                store.append(store_data["location"]["postal_code"])
                store.append("US")
                store.append(store_data["id"])
                location_details = list(BeautifulSoup(store_data["content"],"lxml").stripped_strings)
                for i in range(len(location_details)):
                    if location_details[i] == "Phone":
                        phone = location_details[i+1]
                        break
                store.append(phone)
                store.append("cristy's pizza")
                store.append(store_data["location"]["lat"])
                store.append(store_data["location"]["lng"])
                store.append(hours_object[phone])
                del hours_object[phone]
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
