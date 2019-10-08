import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         'raw_address'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.fourseasons.com"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("ul", {"class": "Navigation-mainLinks"}):
            semi_part = parts.find_all("li", {"class": "Navigation-item"})[0]
            store_request = requests.get(base_url + semi_part.find("a")['href'])
            store_soup = BeautifulSoup(store_request.text, "lxml")
            for in_semi_part in store_soup.find_all("div",{"class": "LinksList-linkContainer"}):
                store_re = requests.get(base_url + in_semi_part.find("a")['href'])
                main_store_soup = BeautifulSoup(store_re.text, "lxml")

                inner_semi_part = main_store_soup.find("div", {"id": "LocationBar"})
                temp_storeaddresss = list(inner_semi_part.stripped_strings)

                return_object = []
                address = temp_storeaddresss[0]

                if('Location' in temp_storeaddresss):
                    temp_storeaddresss.remove('Location')

                if(len(temp_storeaddresss) == 1):
                    phone = '<MISSING>'
                else:
                    phone = temp_storeaddresss[1]
                return_object.append(base_url)
                return_object.append("<INACCESSIBLE>")
                return_object.append("<INACCESSIBLE>")
                return_object.append("<INACCESSIBLE>")
                return_object.append("<INACCESSIBLE>")
                return_object.append("<INACCESSIBLE>")
                return_object.append("US")
                return_object.append("<INACCESSIBLE>")
                return_object.append(phone)
                return_object.append("four seasons")
                return_object.append("<MISSING>")
                return_object.append("<MISSING>")
                return_object.append("<MISSING>")
                return_object.append(address)
                return_main_object.append(return_object)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
