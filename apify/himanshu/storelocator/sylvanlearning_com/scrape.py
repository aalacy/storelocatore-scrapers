import csv
import requests
from bs4 import BeautifulSoup
import re
import io
import json
import time

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
    base_url = "https://www.sylvanlearning.com/locations"
    r = requests.get(base_url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('div', {'class', 'byCountry'})
    for data in exists.findAll('a'):
        if data.get('href') is not None:
            data_url = "https://www.sylvanlearning.com" + data.get('href')
            print(data_url)
            detail_url = requests.get(data_url, headers=headers, verify=False)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            if detail_soup.find('div', {'class', 'locationResults'}):
                for values in detail_soup.findAll('div', {'class', 'locationResults'}):
                    if values.find('div', {'class', 'locationName'}):
                        location_name = values.find('div', {'class', 'locationName'}).get_text().strip().replace("\n", " ")
                        print(location_name)
                        address = re.sub(' +', ' ', values.find('div', {'class', 'locationAddress'}).find('p').get_text().strip().replace("\r\n", ' ').strip().replace("\n", ",").strip()).split(',')
                        street_address = ' '.join(address[:-2])
                        city = address[-3].strip()
                        if len(address[-2].strip().split(' ')) == 2:
                            state = address[-2].strip().split(' ')[0]
                            zip = address[-2].strip().split(' ')[1]
                        else:
                            state = "<MISSING>"
                            zip = "<MISSING>"
                        phone = address[-1]
                        store = []
                        store.append(data_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zip)
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(phone)
                        store.append("Sylvan Learning")
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                        return_main_object.append(store)
                    else:
                        pass
            else:
                pass
        else:
            pass
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()