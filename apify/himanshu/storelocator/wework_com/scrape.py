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
    base_url = "https://www.wework.com/locations"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.find('div', {'class', 'countryList__ScrollContainer-mkgten-0'})
    if exists:
        i = 0
        for data in exists.findAll('a'):
            city = data.get_text()
            print("================================================")
            print("https://www.wework.com" + data.get('href'))
            print("================================================")
            detail_url = requests.get("https://www.wework.com" + data.get('href'), headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            if detail_soup.findAll('a', {'class', 'ray-card--link'}):
                for details in detail_soup.findAll('a', {'class', 'ray-card--link'}):
                    print(i)
                    print("----------------------------------------------------------------------")
                    print("https://www.wework.com" + details.get('href'))
                    print("----------------------------------------------------------------------")
                    detail_page_url = requests.get("https://www.wework.com" + details.get('href'), headers=headers)
                    detail_page_soup = BeautifulSoup(detail_page_url.text, "lxml")
                    if detail_page_soup.find('address', {'class', 'building-address'}):
                        location_name = detail_page_soup.find('h1').get_text().strip()
                        address = detail_page_soup.find('address', {'class', 'building-address'}).get_text().strip().replace('\n', '').replace('        ', ' ').split(' ')
                        street_address = ' '.join(address[:-2][:-1])
                        state = address[-2]
                        zip = address[-1]
                        if detail_page_soup.find('span', {'class', 'ray-text--body-small'}):
                            if detail_page_soup.find('span', {'class', 'ray-text--body-small'}).find('a'):
                                if detail_page_soup.find('span', {'class', 'ray-text--body-small'}).find('a').get_text().strip()[-1].isdigit():
                                    phone = detail_page_soup.find('span', {'class', 'ray-text--body-small'}).find('a').get_text().strip()
                            else:
                                pass
                        else:
                            phone = "<MISSING>"
                        store = []
                        store.append("https://www.wework.com" + details.get('href'))
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zip)
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(phone)
                        store.append("WeWork")
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                        return_main_object.append(store)
                    else:
                        print("Not Found")
                        pass
                i = i + 1
            else:
                print("Not Found detail URL")
                pass
        return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
