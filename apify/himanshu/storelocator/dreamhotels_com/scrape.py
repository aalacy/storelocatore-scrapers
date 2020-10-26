import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    base_url = "https://www.dreamhotels.com/default-en.html"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    for data in soup.find('div', {'class', 'destinationav'}).findAll('a'):
        if data.get('href') == "" or data.get('href') is None or "destinations-en" in data.get('href') or "http://www.dreamhotelgroup.com/" == data.get('href'):
            pass
        else:
            print(data.get('href'))
            detail_url = session.get(data.get('href'), headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            address = detail_soup.select('.footer-directions-text')[0].get_text().strip().replace('\n', ',').split(',')
            if len(address) == 3:
                location_name = address[0]
                street_address = ' '.join(address[-2].split(' ')[:-2])
                city = address[-2].split(' ')[-3]
                state = address[-2].split(' ')[-2]
                zip = address[-2].split(' ')[-1]
                phone = address[-1].split(":")[1].strip()
            elif len(address) == 5:
                location_name = address[0]
                street_address = ' '.join(address[:-2])
                city = address[-3].strip()
                state = address[-2].split(' ')[-2]
                zip = address[-2].split(' ')[-1]
                if 'or' in address[-1].split(":")[1].strip():
                    phone = address[-1].split(":")[1].strip().split('or')[0].strip()
                else:
                    address[-1].split(":")[1].strip()
            elif len(address) == 7:
                if "Email: " in address[-1]:
                    location_name = address[0]
                    street_address = ' '.join(address[:-2])[14:]
                    city = address[-2].strip().split(' ')[0]
                    state = "TH"
                    zip = address[-1].split('-')[0].strip().split(' ')[-1]
                    phone = address[-1].split('-')[0].strip().split(':')[1].strip()
                else:
                    location_name = address[0]
                    street_address = ' '.join(address[1:][:-2])
                    city = address[-3].strip()
                    if address[-2].split(' ')[-1] == "THAILAND":
                        state = "TH"
                    else:
                        state = address[-2].split(' ')[-1]
                    zip = address[-2].strip().split(' ')[0]
                    phone = address[-1].split(":")[1].strip()[1:]
            store = []
            store.append(data.get('href'))
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state.upper())
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Dream Hotels")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()