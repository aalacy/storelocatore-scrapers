from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []

    base_link = "https://www.spunkfitness.com/memberships/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    store_urls = base.find_all(class_="grid-tab-4")
    # Fetch data for each store url

    for store_url in store_urls:
        link = store_url.a['href']
        # Fetch address/phone elements
        location_name = store_url.h4.text
        raw_address = store_url.p.text.split("\n")
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0]
        state = raw_address[1].split(",")[1].split()[0]
        zipcode = raw_address[1].split(",")[1].split()[1]
        phone = store_url.find_all("p")[1].text.strip()

        map_link = store_url.find_all("a")[1]["href"]
        if "@" in map_link:
            at_pos = map_link.rfind("@")
            lat = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
            lon = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
        else:
            lat_pos = map_link.rfind("!3d")
            lat = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
            lng_pos = map_link.find("!4d")
            lon = map_link[lng_pos+3:].strip()

        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        try:
            hours_of_operation = base.table.text.replace("\xa0","").replace("\n"," ")
        except:
            hours_of_operation = base.find(style="font-size:20px").text.replace("Our regular hours of operation are:","").replace("\n"," ").strip()
        hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

        data.append([
            'https://www.spunkfitness.com/',
            link,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            '<MISSING>',
            phone,
            '<MISSING>',
            lat,
            lon,
            hours_of_operation.encode("ascii", "replace").decode().replace("?","-")
        ])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
