import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    main_url = "https://www.cineworld.co.uk"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    r = session.get(main_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    addresses = []
    for script in soup.find_all("script"):
        if "apiSitesList = " in script.text:
            locationList = json.loads(script.text.split("apiSitesList = ")[1].split("}}]")[0]+"}}]")
            for location in locationList:
                location_request = session.get(main_url + location["uri"],headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                phone = ""
                if location_soup.find("cinema-structured-data"):
                    try:
                        phone = location_soup.find("cinema-structured-data")["data-telephone"]
                    except:
                        phone = ""
                address = location["address"]
                street_addrees = ""
                number = location["externalCode"]
                lat = location["latitude"]
                lng = location["longitude"]
                name = location["name"]
                city = address["city"]
                state = address["state"]
                zip_code = address["postalCode"]
                if address["address1"]:
                    street_addrees += address["address1"] + " "
                if address["address2"]:
                    street_addrees += address["address2"] + " "
                if address["address3"]:
                    street_addrees += address["address3"] + " "
                if address["address4"]:
                    street_addrees += address["address4"] + " "
                store = []
                store.append(main_url)
                store.append(name if name else "<MISSING>")
                store.append(street_addrees if street_addrees else "<MISSING>")
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zip_code if zip_code else "<MISSING>")
                store.append("UK")
                store.append(number if number else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append("<MISSING>")
                store.append(main_url + location["uri"])
                for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.strip() if type(x) == str else x for x in store]
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()