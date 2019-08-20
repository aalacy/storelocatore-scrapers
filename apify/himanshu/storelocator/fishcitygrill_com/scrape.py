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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    headers1 = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'referrer': 'https://google.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Pragma': 'no-cache',
    }
    base_url = "https://fishcitygrill.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.find('div', {'class', 'theme-content'})
    if exists:
        for data in exists.findAll('a'):
            print(data.get('href'))
            if "sugarland" not in data.get('href'):
                time.sleep(10)
                detail_page_req = requests.get(data.get('href'), headers=headers1)
                detail_page_soup = BeautifulSoup(detail_page_req.text, "lxml")
                if detail_page_soup.select('.vc_col-sm-6.wpb_column.column_container'):
                    location_name = detail_page_soup.select('.vc_col-sm-6.wpb_column.column_container')[0].find('h2').text
                else:
                    location_name = "<MISSING>"
                hours_of_operation_val = detail_page_soup.select('#text-block-3')[0].get_text().strip().replace("\n\n", ' ').replace("\n", ' ')
                hours_of_operation = ' '.join(hours_of_operation_val.split(' ')[1:])
                full_address = detail_page_soup.select('#text-block-4')[0].find('p').get_text().replace('\n', ' ').strip()
                check_if = full_address.split(' ')
                if len(check_if) > 3:
                    full_address = detail_page_soup.select('#text-block-4')[0].find('p').get_text().replace('\n',' ').strip()
                    if "(" in full_address:
                        street_address = ' '.join(full_address.split(' ')[1:][:-5])
                        city = full_address.split(' ')[1:][-5][:-1]
                        state = full_address.split(' ')[1:][-4]
                        zip = full_address.split(' ')[1:][-3]
                        phone = full_address.split(' ')[1:][-2] + " " + full_address.split(' ')[1:][-1]
                    else:
                        street_address = ' '.join(full_address.split(' ')[1:][:-4])
                        city = full_address.split(' ')[1:][-4][:-1]
                        state = full_address.split(' ')[1:][-3]
                        zip = full_address.split(' ')[1:][-2]
                        phone = full_address.split(' ')[1:][-1]
                else:
                    full_address = detail_page_soup.select('#text-block-4')[0].find('p').find_next('p').get_text().replace('\n',' ').strip()
                    if "(" in full_address:
                        street_address = ' '.join(full_address.split(' ')[1:][:-5])
                        city = full_address.split(' ')[1:][-5][:-1]
                        state = full_address.split(' ')[1:][-4]
                        zip = full_address.split(' ')[1:][-3]
                        phone = full_address.split(' ')[1:][-2] + " " + full_address.split(' ')[1:][-1]
                    else:
                        street_address = ' '.join(full_address.split(' ')[1:][:-4])
                        city = full_address.split(' ')[1:][-4][:-1]
                        state = full_address.split(' ')[1:][-3]
                        zip = full_address.split(' ')[1:][-2]
                        phone = full_address.split(' ')[1:][-1]
            else:
                time.sleep(10)
                detail_page_req = requests.get(data.get('href'), headers=headers1)
                detail_page_soup = BeautifulSoup(detail_page_req.text, "lxml")
                if detail_page_soup.find('div', {'class', 'vc_col-sm-6'}).find('h2'):
                    location_name = detail_page_soup.find('div', {'class', 'vc_col-sm-6'}).find('h2').get_text().strip()
                else:
                    location_name = "<MISSING>"
                hours_of_operation_val = detail_page_soup.select('#text-block-3')[0].get_text().strip().replace("\n\n", ' ').replace("\n", ' ')
                hours_of_operation = ' '.join(hours_of_operation_val.split(' ')[1:])
                full_address = detail_page_soup.select('#text-block-4')[0].find('p').get_text().replace('\n', ' ').strip().split(' ')
                street_address = full_address[1] + " " + full_address[2] + " " + full_address[3]
                city = full_address[-6] + " " + full_address[-5][:-1]
                state = full_address[-4]
                zip = full_address[-3]
                phone = detail_page_soup.select('#text-block-4')[0].find('p').find('a').get('href')[4:]
            store = []
            store.append(data.get('href'))
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Fish City Grill")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append(hours_of_operation)
            return_main_object.append(store)
        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()