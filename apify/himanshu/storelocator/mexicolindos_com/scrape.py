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
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://mexicolindos.com"
    r = session.get("http://mexicolindos.com/locations.php",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_url = []
    for location in soup.find_all("iframe"):
        geo_request = session.get(location["src"],headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
                phone = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][7]
        store_zip_split = re.findall(" ([0-9]{5})",geo_data)
        if store_zip_split:
            store_zip = store_zip_split[-1]
        state_split = re.findall(" ([A-Z]{2}) ",geo_data)
        if state_split:
            state = state_split[-1]
        city = geo_data.split(",")[2]
        store = []
        store.append("http://mexicolindos.com")
        store.append(city)
        store.append(geo_data.split(",")[1])
        store.append(city)
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("mexico lindo")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
