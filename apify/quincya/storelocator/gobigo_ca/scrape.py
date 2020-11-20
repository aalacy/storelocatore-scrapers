import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    base_link = "https://apps.elfsight.com/p/boot/?w=84eca792-36b8-45b6-9851-465cd482c3d2"

    session = SgRequests()
    stores = session.get(base_link, headers = HEADERS).json()['data']['widgets']["84eca792-36b8-45b6-9851-465cd482c3d2"]['data']['settings']['markers']

    data = []
    locator_domain = "bigotiresbroadway.ca"

    for store in stores:
        location_name = store["infoTitle"]
        raw_address = store["position"].split(",")
        street_address = raw_address[0].encode("ascii", "replace").decode().replace("?","-").strip()
        city = raw_address[1].split("BC")[0].strip()
        state = "BC"
        zip_code = raw_address[1].split("BC")[1].replace("*","8").strip().upper()
        if not zip_code:
            zip_code = "<MISSING>"
        country_code = "CA"
        location_type = "<MISSING>"
        phone = store['infoPhone'].strip()
        store_number = "<MISSING>"
        try:
            latitude = store['coordinates'].split(",")[0].strip()
            longitude = store['coordinates'].split(",")[1].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        link = store['infoSite']
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")
        try:
            hours_of_operation = " ".join(list(base.find_all(class_="list simple margin-top-20")[-1].stripped_strings))
        except:
            try:
                hours_of_operation = base.find(class_="ourloc wrapper").find_all("p")[-1].text.strip()
            except:
                try:
                    hours_of_operation = base.find(class_="locwidget-hours").text.replace("Hours:","").strip()
                except:
                    hours_of_operation = "<MISSING>"

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
