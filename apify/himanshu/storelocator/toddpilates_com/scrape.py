import csv
import requests
from bs4 import BeautifulSoup
import re
import json

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
    base_url = "https://www.toddpilates.com"
    r = requests.get("https://www.toddpilates.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_url = []
    for location in soup.find("nav",{'class':"w-dropdown-list"}).find_all("a"):
        name = location.text.strip()
        location_request = requests.get(base_url + location['href'],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        yelp_url = location_soup.find("a",{"href":re.compile("yelp.com")})["href"]
        yelp_request = requests.get(yelp_url,headers=headers)
        yelp_soup = BeautifulSoup(yelp_request.text,"lxml")
        for script in yelp_soup.find_all("script",{"type":"application/ld+json"}):
            if "address" in script.text:
                location_details = json.loads(script.text)
        hours = " ".join(list(yelp_soup.find("table",{"class":"table table-simple hours-table"}).stripped_strings))
        store = []
        store.append("https://www.toddpilates.com")
        store.append(location_details["name"])
        store.append(location_details["address"]["streetAddress"].replace("\n",","))
        store.append(location_details["address"]["addressLocality"])
        store.append(location_details["address"]["addressRegion"])
        store.append(location_details["address"]["postalCode"])
        store.append(location_details["address"]["addressCountry"])
        store.append("<MISSING>")
        store.append(location_details["telephone"] if location_details["telephone"] else "<MISSING>")
        store.append("tod pilates & barre")
        geo = json.loads(yelp_soup.find("div",{'class':"lightbox-map"})["data-map-state"])
        store.append(geo["center"]["latitude"])
        store.append(geo["center"]["longitude"])
        store.append(hours)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()