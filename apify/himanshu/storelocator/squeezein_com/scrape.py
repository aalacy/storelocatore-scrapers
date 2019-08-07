import csv
import requests
from bs4 import BeautifulSoup
import re
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

    print("soup ===  first")

    base_url = "https://www.squeezein.com"
    r = requests.get("https://www.squeezein.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "squeezein"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find_all("div", {'class': 'intrinsic'}):
        # print("script.find('a') ==================== "+  str(script.find('a')))

        if script.find('a') is not None:
            store_url = script.find('a')['href']
            if store_url[0] == "/":
                store_url = base_url + store_url

            print('store_url = ' + store_url)
            r_store = requests.get(store_url, headers=headers)
            soup_store = BeautifulSoup(r_store.text, "lxml")

            # location_name = soup_store.find('div', {'class': 'desc-wrapper tmpl-loading'}).find('h1').text
            location_name = soup_store.find('h1', {'class': 'page-title'}).text

            for store_data in soup_store.find_all("div", {'class': 'page-description'}):
                street_address = store_data.find('strong').text
                # print("street_address  == " + str(street_address))
                single_store_data = list(store_data.stripped_strings)

                if 'Order Online' in single_store_data:
                    single_store_data.remove('Order Online')

                if 'NOW OPEN!' in single_store_data:
                    single_store_data.remove('NOW OPEN!')

                print(str(len(single_store_data))+"street_address  == " + str(single_store_data))

                street_address = single_store_data[0]
                city = single_store_data[1].split(',')[0]
                state = single_store_data[1].split(',')[1].split(' ')[-2]
                zipp = single_store_data[1].split(',')[1].split(' ')[-1]

                if len(single_store_data) > 3:
                    phone = single_store_data[2]
                else:
                    phone = '<MISSING>'

                hours_of_operation = single_store_data[-1]

                country_code = 'US'
                store_number = '<MISSING>'
                latitude = '<MISSING>'
                longitude = '<MISSING>'
                location_name = '<MISSING>'

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]

                print("data = " + str(store))
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
