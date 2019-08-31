import csv
import requests
from bs4 import BeautifulSoup
import re
import io
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://skyhighsports.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('div', {'class', 'state'})
    state_dict = {'california': 'CA', 'illinois': 'IL', 'oregon': 'OR', 'tennessee': 'TN'}
    if exists:
        for states in soup.findAll('div', {'class', 'state'}):
            state_name = states.get('class')[1].lower()
            for links in states.find_next('ul').findAll('a'):
                if "http" in links.get('href'):
                    data_url = links.get('href')
                    detail_url = requests.get(data_url, headers=headers)
                    detail_soup = BeautifulSoup(detail_url.text, "lxml")
                    if detail_soup.select('#hours'):
                        if detail_soup.select('.phone_number'):
                            phone = detail_soup.select('.phone_number')[0].get_text().strip().replace('JUMP','')
                            state = state_dict[state_name]
                        else:
                            phone = "<MISSING>"
                        if detail_soup.select('.welcome'):
                            location_name = detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0]
                            if "," in detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0]:
                                city = detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0].split(',')[0]
                            elif "/" in detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0]:
                                city = detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0].split('/')[0]
                            else:
                                city = detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0]
                        else:
                            city = "<MISSING>"
                        if detail_soup.select('#hours'):
                            hours_of_operation = detail_soup.select('#hours')[0].get_text().replace("\n\n\n", ' ').replace('\n', ' ').strip()
                        else:
                            hours_of_operation = "<MISSING>"
                        store = []
                        store.append(data_url)
                        store.append(location_name)
                        store.append("<MISSING>")
                        store.append(city)
                        store.append(state)
                        store.append("<MISSING>")
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(phone)
                        store.append("Sky High Sports")
                        store.append("<INACCESSIBLE>")
                        store.append("<INACCESSIBLE>")
                        store.append(hours_of_operation)
                        return_main_object.append(store)
                    else:
                        pass
                else:
                    pass
        return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
