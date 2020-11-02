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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.mylsb.com"
    r = session.get("https://www.mylsb.com/locations/default.aspx",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    links = []
    for location in soup.find("div",{'class':"base_bg"}).find_all("a",{'href':re.compile("/locations/")}):
        if location["href"] in links:
            continue
        links.append(location["href"])
        location_reqeust = session.get(base_url + location["href"])
        location_soup = BeautifulSoup(location_reqeust.text,"lxml")
        name = location_soup.find("h1").text.strip()
        street_address = location_soup.find("span",{'itemprop':"streetAddress"}).text.strip()
        city = location_soup.find("span",{'itemprop':"addressLocality"}).text.strip()
        state = location_soup.find("span",{'itemprop':"addressRegion"}).text.strip()
        store_zip = location_soup.find("span",{'itemprop':"postalCode"}).text.strip()
        phone = location_soup.find_all("a",{'href':re.compile("tel:")})[1].text.strip()
        location_details = list(location_soup.find("div",{'class':'location_detail'}).stripped_strings)[:-1]
        if "location" in location_details:
            del location_details[-1]
        for i in range(len(location_details)):
            if location_details[i] == "Hours":
                hours = " ".join(location_details[i+1:])
                break
        store = []
        store.append("https://www.mylsb.com")
        store.append(name)
        store.append(street_address.replace("\t"," ").replace("\n"," ").replace("\t"," "))
        store.append(city)
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("lincoln bank")
        geo_lcoation = location_soup.find_all("iframe")[-1]["src"]
        if "!3d" in geo_lcoation:
            store.append(geo_lcoation.split("!3d")[1].split("!")[0])
            store.append(geo_lcoation.split("!2d")[1].split("!")[0])
        else:
            for script in location_soup.find_all("script"):
                if "var locations = " in script.text:
                    store.append(script.text.split('"lat":')[1].split(",")[0])
                    store.append(script.text.split('"long":')[1].split(",")[0])
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
