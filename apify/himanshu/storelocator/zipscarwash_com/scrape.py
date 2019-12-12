import csv
import requests
import json
import sgzip
from bs4 import BeautifulSoup
# import time
# from random import randrange
import re


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.zipscarwash.com"
    return_main_object = []
    addresses = []
    r = requests.get('https://www.zipscarwash.com/search-by-state')
    soup = BeautifulSoup(r.text, 'lxml')
    select = soup.find('select', {'name': 'field_address_administrative_area'})
    for option in select.find_all('option'):
        if "All" not in option['value']:
            state_code = option['value']
            # print('https://www.zipscarwash.com/search-by-state?field_address_administrative_area=' + str(state_code))
            loc_r = requests.get(
                'https://www.zipscarwash.com/search-by-state?field_address_administrative_area=' + str(state_code))
            soup = BeautifulSoup(loc_r.text, 'lxml')
            for loc in soup.find_all('div', class_='address-column'):
                for col in loc.find_all('div', class_='views-col'):
                    locator_domain = base_url
                    store_number = "<MISSING>"
                    location_type = "<MISSING>"
                    page_url = base_url + \
                        col.find('div', class_='views-field-title').a['href']
                    location_name = col.find(
                        'div', class_='views-field-title').text.split('(')[0].strip()
                    # city = location_name.split(',')[0].strip()
                    # state = location_name.split(',')[-1].strip()
                    street_address = col.find('p', class_='address').find(
                        'span', class_='address-line1').text.strip()
                    city = col.find('p', class_='address').find(
                        'span', class_='locality').text.strip()
                    state = col.find('p', class_='address').find(
                        'span', class_='administrative-area').text.strip()
                    zipp = col.find('p', class_='address').find(
                        'span', class_='postal-code').text.strip()
                    # country_code = col.find('p', class_='address').find(
                    #     'span', class_='country').text.strip()
                    country_code = "US"
                    if col.find('div', class_='views-field-field-phone-no') != None:
                        phone = col.find(
                            'div', class_='views-field-field-phone-no').text.strip().replace('Phone:', '').strip()
                    else:
                        phone = "<MISSING>"
                    if col.find('div', class_='views-field-field-location-hours') != None:
                        hours_of_operation = col.find(
                            'div', class_='views-field-field-location-hours').text.strip().replace('Hours: ', '').strip()
                    else:
                        hours_of_operation = "<MISSING>"
                    direction = col.find(
                        "div", text=re.compile("Directions")).a['href']
                    latitude = direction.split(
                        '?')[-1].split('&')[0].split('=')[-1].strip()
                    longitude = direction.split(
                        '?')[-1].split('&')[-1].split('=')[-1].strip()
                    store = []

                    store.append(locator_domain)
                    store.append(
                        location_name if location_name else "<MISSING>")
                    store.append(
                        street_address if street_address else "<MISSING>")
                    store.append(city if city else "<MISSING>")
                    store.append(state if state else "<MISSING>")
                    store.append(zipp if zipp else "<MISSING>")
                    store.append(country_code if country_code else "<MISSING>")
                    store.append(store_number if store_number else "<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append(
                        location_type if location_type else "<MISSING>")
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(longitude if longitude else "<MISSING>")
                    store.append(
                        hours_of_operation if hours_of_operation else "<MISSING>")
                    store.append(page_url if page_url else "<MISSING>")
                    if store[2] in addresses:
                        continue

                    addresses.append(store[2])
                    #print("===", str(store))
                    #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    # return_main_object.append(store)
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
