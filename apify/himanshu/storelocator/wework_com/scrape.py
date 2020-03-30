import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import unicodedata
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.wework.com/locations"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    for country in soup.find_all("h3"):
        if country.text == "United States":
            country_code = "US"
        elif country.text == "Canada":
            country_code = "US"
        else:
            continue
        for city in country.find_next_sibling("ul").find_all("a"):
            city_request = session.get("https://www.wework.com" + city["href"],headers=headers)
            city_soup = BeautifulSoup(city_request.text,"lxml")
            for locaion in city_soup.find_all("a",{"class":'ray-card'}):
                page_url = "https://www.wework.com" + locaion["href"]
                location_request = session.get(page_url,headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                for script in location_soup.find_all("script",{"type":'application/ld+json'}):
                    json_data = json.loads(script.text)
                    if "address" in json_data:
                        break
                name = location_soup.find("div",{"class":'lead-form-building-name'}).text.strip()
                store = []
                store.append("https://www.wework.com")
                store.append(name)
                store.append(json_data["address"]["streetAddress"].split("\n")[0])
                store.append(json_data["address"]["addressLocality"] if json_data["address"]["addressLocality"] else "<MISSING>")
                store.append(json_data["address"]["addressRegion"] if json_data["address"]["addressRegion"] else "<MISSING>")
                store.append(json_data["address"]["postalCode"] if json_data["address"]["postalCode"] else "<MISSING>")
                store.append(json_data["address"]["addressCountry"])
                store.append("<MISSING>")
                store.append(json_data["telephone"] if json_data["telephone"] else "<MISSING>")
                store.append("<MISSING>")
                store.append(json_data["geo"]["latitude"])
                store.append(json_data["geo"]["longitude"])
                store.append("<MISSING>")
                store.append(page_url)
                for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
