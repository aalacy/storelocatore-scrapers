import csv
import requests
from bs4 import BeautifulSoup
import re
import io
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://beardpapas.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.find('ul', {'class', 'footer_loc'})
    if exists:
        for data in exists.findAll('li'):
            detail_url = requests.get(data.find('a').get('href'), headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            detail_pages = detail_soup.findAll('div', {'class', 'location-block'})
            for detail_page in detail_pages:
                detail_page_url = requests.get(detail_page.find('a', {'class', 'viewbtn'}).get('href'), headers=headers)
                detail_soup = BeautifulSoup(detail_page_url.text, "lxml")
                if detail_soup.find('div', {'class', 'heading'}):
                    location_name = detail_soup.find('div', {'class', 'heading'}).text.strip()
                else:
                    location_name = "<MISSING>"
                if detail_soup.find('div', {'class', 'location_details'}):
                    address = detail_soup.find('div', {'class', 'location_details'}).find('p').text.strip().split(',')
                    street_address = ' '.join(address[:-1])
                    city = location_name
                    state = address[-1].strip().split(' ')[0]
                    zip_val = address[-1].strip().split(' ')[1]
                    if "-" in zip_val:
                        zip = zip_val.split('-')[0]
                    else:
                        zip = zip_val
                    phone = detail_soup.find('div', {'class', 'location_details'}).find_next('img').find_next('a').get('href')[4:].strip()
                    if detail_soup.find('div', {'class', 'location_direction'}).find('a').get('href'):
                        if "@" in detail_soup.find('div', {'class', 'location_direction'}).find('a').get('href'):
                            latitude =  detail_soup.find('div', {'class', 'location_direction'}).find('a').get('href').split('@')[1].split(',')[0]
                            longitude =  detail_soup.find('div', {'class', 'location_direction'}).find('a').get('href').split('@')[1].split(',')[1]
                        else:
                            latitude = "<MISSING>"
                            longitude = "<MISSING>"
                    hours_of_operation =  detail_soup.findAll('div', {'class', 'location_details'})[-1].find('div', {'class', 'location_last_inner'}).get_text().replace('\n\n', '').replace('\n', '').replace('\r', '').strip()
                else:
                    pass
                store = []
                store.append("https://beardpapas.com")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(detail_page.find('a', {'class', 'viewbtn'}).get('href'))
                return_main_object.append(store)
        other = soup.find('ul', {'class', 'footer_loc'}).find_next('ul')
        for data in other.findAll('li'):
            detail_url = requests.get(data.find('a').get('href'), headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            detail_pages = detail_soup.findAll('div', {'class', 'location-block'})
            for detail_page in detail_pages:
                detail_page_url = requests.get(detail_page.find('a', {'class', 'viewbtn'}).get('href'), headers=headers)
                detail_soup = BeautifulSoup(detail_page_url.text, "lxml")
                if detail_soup.find('div', {'class', 'heading'}):
                    location_name = detail_soup.find('div', {'class', 'heading'}).text.strip()
                else:
                    location_name = "<MISSING>"
                if detail_soup.find('div', {'class', 'location_details'}):
                    if "canada" not in data.find('a').get('href'):
                        address = detail_soup.find('div', {'class', 'location_details'}).find('p').text.strip().split(',')
                        street_address = ' '.join(address[:-1])
                        city = location_name
                        state = address[-1].strip().split(' ')[0]
                        zip = address[-1].strip().split(' ')[1]
                    else:
                        city = location_name
                        address = detail_soup.find('div', {'class', 'location_details'}).find('p').text.strip().split(',')
                        if address[-1].strip()[-1:].isdigit():
                            street_address = address[0].strip()
                            state = address[1].strip().split(' ')[0]
                            zip = ' '.join(address[1].strip().split(' ')[1:])
                        else:
                            street_address = ' '.join(address[:-2])
                            state = address[-2].strip().split(' ')[0]
                            zip = ' '.join(address[-2].strip().split(' ')[1:])
                    phone = detail_soup.find('div', {'class', 'location_details'}).find_next('img').find_next('a').get('href')[4:].strip()
                    if detail_soup.find('div', {'class', 'location_direction'}).find('a').get('href'):
                        if "@" in detail_soup.find('div', {'class', 'location_direction'}).find('a').get('href'):
                            latitude =  detail_soup.find('div', {'class', 'location_direction'}).find('a').get('href').split('@')[1].split(',')[0]
                            longitude =  detail_soup.find('div', {'class', 'location_direction'}).find('a').get('href').split('@')[1].split(',')[1]
                        else:
                            latitude = "<MISSING>"
                            longitude = "<MISSING>"
                    hours_of_operation =  detail_soup.findAll('div', {'class', 'location_details'})[-1].find('div', {'class', 'location_last_inner'}).get_text().replace('\n\n', '').replace('\n', '').replace('\r', '').strip()
                else:
                    pass
                store = []
                store.append("https://beardpapas.com")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(detail_page.find('a', {'class', 'viewbtn'}).get('href'))
                return_main_object.append(store)
        return return_main_object
    else:
        pass

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
