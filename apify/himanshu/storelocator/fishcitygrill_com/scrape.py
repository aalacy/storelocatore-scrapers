import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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
    url = "https://fishcitygrill.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.find('div', {'class', 'theme-content'})
    if exists:
        for data in exists.findAll('a'):
            page_url = data.get('href')
            locator_domain = "https://fishcitygrill.com/"
            location_name = data.text.replace(
                '– NOW OPEN!', '').replace('&', '').strip()
            # print(location_name)
            r_loc = session.get(page_url, headers=headers1)
            soup_loc = BeautifulSoup(r_loc.text, 'lxml')
            # div = soup_loc.find('div', class_='mk-main-wrapper-holder')
            # info = div.find('div', class_='vc_column-inner ')
            tag_hours = soup_loc.find(lambda tag: (
                tag.name == "strong") and "Hours:" == tag.text.strip())
            if tag_hours != None:
                hours_list = list(tag_hours.parent.parent.stripped_strings)
                hours_list = [el.replace('\xa0', ' ') for el in hours_list]
                hours_of_operation = " ".join(
                    hours_list).replace("Hours:", "").strip()
            else:
                hours_of_operation = "<MISSING>"
            tag_address = soup_loc.find(lambda tag: (
                tag.name == "strong" or tag.name == "b") and "Address:" == tag.text.strip())

            address_list = list(tag_address.parent.parent.stripped_strings)
            if "Address:" in " ".join(address_list):
                address_list.remove('Address:')
            if address_list != []:
                phone_list = re.findall(re.compile(
                    ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(address_list[-1]))
                if phone_list:
                    phone = phone_list[-1].strip()
                else:
                    phone = "<MISSING>"
                street_address = " ".join(address_list[:-2]).strip()
                # print(street_address)
                city = address_list[-2].split(',')[0].strip()
                state = " ".join(
                    address_list[-2].split(',')[-1].split()[:-1]).strip()
                zipp = address_list[-2].split(',')[-1].split()[-1].strip()
            else:
                address_list = tag_address.parent.parent.find_next('p')
                list_add = list(address_list.stripped_strings)
                phone_list = re.findall(re.compile(
                    ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_add[-1]))
                if phone_list:
                    phone = phone_list[-1].strip()
                else:
                    phone = "<MISSING>"
                street_address = " ".join(list_add[:-2]).strip()
                # print(street_address)
                city = list_add[-2].split(',')[0].strip()
                state = " ".join(
                    list_add[-2].split(',')[-1].split()[:-1]).strip()
                zipp = list_add[-2].split(',')[-1].split()[-1].strip()
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            iframe = soup_loc.find('iframe')['src']
            latitude = iframe.split('!2d')[1].split('!3d')[
                1].split('!')[0].strip()
            longitude = iframe.split('!2d')[1].split('!3d')[0].strip()

            store = []
            store.append(locator_domain)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            # print('data ==' + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
