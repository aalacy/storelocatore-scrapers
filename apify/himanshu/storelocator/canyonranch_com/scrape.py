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
    base_url = "https://www.canyonranch.com"
    r = session.get("https://www.canyonranch.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    addresses = []
    for location in soup.find("ul",{'id':"menu-main-menu"}).find_all("a"):
        location_request = session.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_detail_request = session.get(location_soup.find("a",{'href':re.compile("plan")})['href'],headers=headers)
        location_detail_soup = BeautifulSoup(location_detail_request.text,"lxml")
        geo_request = session.get(location_detail_soup.find_all("iframe")[-1]["src"],headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][13]
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
                name = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][1]
        store_zip_split = re.findall(" ([0-9]{5})",geo_data)
        if store_zip_split:
            store_zip = store_zip_split[0]
        state_split = re.findall(" ([A-Z]{2}) ",geo_data)
        if state_split:
            state = state_split[0]
        city = geo_data.split(",")[1]
        phone = location_detail_soup.find("a",{"href":re.compile("tel:")})["href"].split("tel:")[1]
        store = []
        store.append("https://www.canyonranch.com")
        store.append(name.replace("–","-"))
        store.append(geo_data.split(",")[0])
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        store.append(city)
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("canyon ranch")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()