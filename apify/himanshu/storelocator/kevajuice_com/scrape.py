import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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

    base_url = "http://kevajuice.com/"

    addresses = []
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
    country_code = "US"
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = ""

    # for script in soup.find_all("div", {'class': re.compile('tp-caption')}):
    #     store_url = script.find('a')['href']
    #     print("store_url == " + store_url)

    list_store_url = []
    r = requests.get("http://kevajuice.com/store-locator/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for script in soup.find_all("div", {'class': re.compile('tp-caption')}):
        list_store_url.append(script.find('a')['href'])
        list_store_url = list(dict.fromkeys(list_store_url))

    for store_url in list_store_url:
        if "nevada" not in store_url:

            r_store = requests.get(store_url, headers=headers)
            soup_store = BeautifulSoup(r_store.text, "lxml")
            table = soup_store.find('table')
            # print(table)
            for tr in table.find_all('tr')[1:]:
                page_url = store_url
                address = list(tr.find_all('td')[0].stripped_strings)
                # print(address)
                # print('~~~~~~~~~~~~~~')
                if address == []:
                    location_name = "<MISSING>"
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                elif len(address) == 1:
                    location_name = address[0].strip()
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                else:
                    location_name = address[0].strip()
                    street_address = " ".join(address[1:-1]).strip()
                    city = address[-1].split(',')[0].strip()
                    state = address[-1].split(',')[-1].split()[0].strip()
                    zipp = address[-1].split(',')[-1].split()[-1].strip()
                hours_of_operation = " ".join(
                    list(tr.find_all('td')[1].stripped_strings)).strip().replace("Follows Airport Hours", "").replace("Follows Mall Hours ", "").replace("May vary", "").strip()
                phone = list(tr.find_all('td')[2].stripped_strings)[0].strip()
                coord = tr.find_all('td')[3].a['href']
                if "&sll" in coord:
                    latitude = coord.split("&sll=")[1].split(',')[0]
                    longitude = coord.split("&sll=")[1].split(',')[
                        1].split('&')[0]
                else:

                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = ["<MISSING>" if x == "" else x for x in store]
                store = [str(x).encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]

                if store[1] + " " + store[2] in addresses:
                    continue
                addresses.append(store[1] + " " + store[2])
                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
