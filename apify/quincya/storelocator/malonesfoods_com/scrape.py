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
    
    base_link = "http://www.malonesfoods.com/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)

    try:
        base = BeautifulSoup(req.text,"lxml")
    except (BaseException):
        print ('[!] Error Occured. ')
        print ('[?] Check whether system is Online.')

    items = base.find_all(class_="wsite-multicol-table")[-1].find_all(class_="paragraph")

    data = []
    for item in items:

        locator_domain = "malonesfoods.com"
        
        raw_data = item.text.replace("Main Office","").replace("\xa0 \xa0","\xa0").split("\xa0")
        location_name = raw_data[0].strip()
        print(location_name)
        if "#" in location_name:
            store_number = location_name[location_name.find("#")+1:].strip()
            location_type = "Store"
        else:
            store_number = "<MISSING>"
            location_type = "Main Office"

        street_address = raw_data[1].strip()
        raw_line = raw_data[2].strip()
        city = raw_line[:raw_line.rfind(',')].strip()
        state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
        zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
        country_code = "US"
        
        phone = raw_data[3].replace("\u200b","").strip()
        hours_of_operation = "<INACCESSIBLE>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
