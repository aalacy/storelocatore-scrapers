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
    base_url = "https://limefreshmexicangrill.com"
    r = requests.get("https://limefreshmexicangrill.com/wp-content/themes/lime/map.php",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_request = requests.get("https://limefreshmexicangrill.com/lime-locations/",headers=headers)
    location_soup = BeautifulSoup(location_request.text,"lxml")
    location_data = {}
    for location in location_soup.find("aside").find_all("li"):
        name = location.find_all("a")[1].text
        hours = " ".join(list(location.find_all("p")[2].stripped_strings))
        location_data[name] = hours
    for script in soup.find_all("script"):
        if "var mappangea5_data =" in script.text:
            location_list = json.loads((script.text.split("var mappangea5_data =")[1].split("};")[0] + "}").replace("'",'"').split('"locations":')[1].split("]")[0] + "{}]")[:-1]
            for i in range(len(location_list)):
                store_data = location_list[i]
                store = []
                store.append("https://limefreshmexicangrill.com")
                store.append(store_data["name"])
                store.append(store_data["address"])
                store.append(store_data["citystzip"].split(",")[0])
                store.append(store_data["citystzip"].split(",")[1].split(" ")[-2])
                store.append(store_data["citystzip"].split(",")[1].split(" ")[-1])
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["phone"])
                store.append("lime fresh mexican grill")
                store.append(store_data["location"]["lat"])
                store.append(store_data["location"]["lng"])
                store.append(location_data[store_data["phone"]])
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
