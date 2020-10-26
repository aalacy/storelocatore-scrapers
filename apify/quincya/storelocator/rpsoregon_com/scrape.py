from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import json
import re
from random import randint


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    base_link = "https://www.rpsoregon.com/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(2,3))
    try:
        base = BeautifulSoup(req.text,"lxml")
        print("Got today page")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    raw_data = base.find(class_='u_1334673460 dmNewParagraph').find_all('span')[1].find_all('div')

    data = []
    locator_domain = "rpsoregon.com"
    country_code = "US"
    store_number = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = base.find(class_="open-hours-data").text.replace("\n"," ").strip()

    street_address = ""
    for i, row in enumerate(raw_data):
        row = raw_data[i]
        row_txt = row.text.strip()

        if i ==0:
            location_name = row_txt
            phone = raw_data[i+1].text
        elif ',' in row_txt:
            city_line = row_txt.replace("NESalem","NE, Salem")
            if not street_address:
                street_address = city_line[:city_line.find(",")].strip()
            city_line = city_line.replace(street_address,"")
            city = city_line[:city_line.rfind(',')].replace(",","").strip()
            if "OR" in city_line:
                state = 'OR'
            else:
                state = "<MISSING>"
            zip_code = city_line[-6:].strip()
            if not zip_code.isnumeric():
                zip_code = "<MISSING>"
            data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
        elif "(" not in row_txt:
                street_address = (street_address + " " + row_txt).replace("CORVALLIS","").strip()
        if not row_txt:
            location_name = raw_data[i+1].text
            phone = raw_data[i+2].text
            street_address = ""

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

