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
    base_url = "http://fayettepartsservice.com"
    r = requests.get("http://fayettepartsservice.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "restore" in script.text:
            data = json.loads(re.sub(r'(?<={|,)([a-zA-Z][a-zA-Z0-9]*)(?=:)', r'"\1"',script.text.split("restore: ")[1].split("}}]}]}")[0] + '}}]}]}'),strict=False)["groups"][0]["pins"]
            for i in range(len(data)):
                store_data = data[i]
                location_details = list(BeautifulSoup(store_data["label"]["content"],"lxml").stripped_strings)
                if location_details[-1] == "Directions to Store":
                    del location_details[-1]
                store = []
                store.append("http://fayettepartsservice.com")
                store.append(location_details[0])
                store.append(location_details[1])
                store.append(location_details[2].split(",")[0])
                store.append(location_details[2].split(",")[1].split(" ")[-2])
                store.append(location_details[2].split(",")[1].split(" ")[-1])
                store.append("US")
                store.append(store_data["PID"])
                store.append(location_details[3])
                store.append("fayette parts service")
                store.append(store_data["location"]["lat"])
                store.append(store_data["location"]["lng"])
                store.append(" ".join(location_details[5:]))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
