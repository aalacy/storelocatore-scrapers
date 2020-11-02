from bs4 import BeautifulSoup
from sgrequests import SgRequests
import re
import csv
import time


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    session = SgRequests()

    location_url = 'https://bkpilates.com/contact'
    locator_domain = 'bkpilates.com'

    page = session.get(location_url)
    time.sleep(2)
    assert page.status_code == 200

    content = BeautifulSoup(page.content, 'html.parser')

    location_data = content.find('div', {'class':'sqs-block-content'}).find_all("p")[1:]

    data = []
    last_poi = False
    for i, store in enumerate(location_data):
        if not last_poi:
            store_str = str(store)
            raw_data = store_str.split("<br/>")
            try:
                store_name = raw_data[0][raw_data[0].find("strong")+7:raw_data[0].rfind("<")].strip()
                street_add = raw_data[1].replace(",","").replace("</p>","").strip()
            except:
                continue
            if "Phone" in store_str:
                city_line = raw_data[2]
                phone = raw_data[3].replace(",","").replace("Phone: ","").replace("</p>","").strip()
            else:
                city_line = location_data[i+1].text.strip()
                phone = location_data[i+2].text.replace("Phone: ","").replace("</p>","").strip()
                last_poi = True
            state = city_line[city_line.rfind(" ")-3:city_line.rfind(" ")].strip()
            zip_code = city_line[city_line.rfind(" ")+1:].strip()
            city = city_line[:city_line.rfind(" ")-3].strip()
            country_code = "US"

            raw_hours = content.find(class_="Footer-inner clear").text
            raw_hours = raw_hours[raw_hours.find("Mon "):raw_hours.rfind("00pm")+4]
            if store_name == "BK Pilates Brooklyn":
                hours = raw_hours[:raw_hours.find("FLATIRON")].replace("pm","pm ").strip()
            elif store_name == "BK Pilates Flatiron":
                hours = raw_hours[raw_hours.find("_Mon")+1:raw_hours.find("TRIBECA")].replace("pm","pm ").strip()
            elif store_name == "BK Pilates Tribeca":
                hours = raw_hours[raw_hours.rfind("_Mon")+1:].replace("pm","pm ").strip()
            else:
                hours = "<MISSING>"

            location_type = "<MISSING>"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            data.append([locator_domain, location_url, store_name, street_add, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


