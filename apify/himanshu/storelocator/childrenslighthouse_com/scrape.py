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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://childrenslighthouse.com/find-a-daycare"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('select', {'class', 'all_regions_list'})
    if exists:
        for data in exists.findAll('option'):
            if data.get('value') is None:
                if "area" in data.get_text():
                    pass
                else:
                    state = data.get_text().strip()
            else:
                data_url = "https://childrenslighthouse.com/" + data.get('value').strip()
                print(data_url)
                city = data.get_text().strip()
                soup_url = requests.get(data_url, headers=headers)
                detail_soup = BeautifulSoup(soup_url.text, "lxml")
                detail_exists = detail_soup.find('section', {'class', 'regions_list'})
                if detail_exists:
                    for values in detail_exists.findAll('div', {'class', 'region_location'}):
                        if values.select('.region_loc_title_holder'):
                            location_name = values.select('.region_loc_title_holder')[0].get_text().strip()
                        else:
                            location_name = "<MISSING>"
                        if values.select('.region_loc_phone'):
                            phone = values.select('.region_loc_phone')[0].get_text().strip()
                            if len(phone) < 2:
                                phone = "<MISSING>"
                            else:
                                phone = values.select('.region_loc_phone')[0].get_text().strip()
                        else:
                            phone = "<MISSING>"
                        if values.select('.region_loc_address'):
                            adddress = values.select('.region_loc_address')[0].get_text().strip().replace('\n\t\t\t\t\t\t', '').strip().split(',')
                            street_address = adddress[0]
                            state = adddress[-1].strip().split(' ')[0]
                            zip = adddress[-1].strip().split(' ')[1]
                        else:
                            street_address = "<MISSING>"
                            state = "<MISSING>"
                            zip = "<MISSING>"
                        store = []
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zip)
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(phone)
                        store.append("Child Day Care - Children's Lighthouse")
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                        return_main_object.append(store)
                else:
                    pass
        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)
scrape()