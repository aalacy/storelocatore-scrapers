import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    }
    base_url = "https://rotolos.com"
    r = session.get("https://rotolos.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("select",{'id':"restaurant-select"}).find_all("option"):
        if "loc_link" not in location.attrs:
            continue
        page_url = location["loc_link"]
        location_request = session.get(page_url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        current_location = location_soup.find(class_='address')
        street_address = current_location.find('span', attrs={'itemprop': "streetAddress"}).text.strip()
        city = current_location.find('span', attrs={'itemprop': "addressLocality"}).text.replace("  "," ").strip()
        if city[-1:] == ",":
            city = city[:-1]
        state = current_location.find('span', attrs={'itemprop': "addressRegion"}).text.strip()
        if state[-1:] == ",":
            state = state[:-1]
        zip_code = current_location.find('span', attrs={'itemprop': "postalCode"}).text.strip()
        phone = current_location.find('span', attrs={'itemprop': "telephone"}).text.strip()
        hours = " ".join(list(location_soup.find("div",{'id':'location-hours'}).stripped_strings)[1:]).replace("–","-").replace("..","").strip()

        map_link = location_soup.find_all(class_="row single-location")[1].find_all("a")[1]["href"]
        try:
            latitude = map_link.split("=")[-1].split(",")[0]
            longitude = map_link.split("=")[-1].split(",")[1]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        if not latitude:
            latitude = "<MISSING>"
            longitude = "<MISSING>"            

        store = []
        store.append("https://rotolos.com")
        store.append(page_url)
        store.append(location_soup.find("h1").text.replace("–","-"))
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zip_code)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
