import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import unicodedata


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
    addresses = []
    base_url = "http://samssoutherneatery.com"
    r = requests.get(
        "https://samssoutherneatery.com/locations-list", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # for a in soup.find("main", {"class": "Index"}).find_all("a"):
    for link in soup.find_all(lambda tag: (tag.name == "a") and "Order Now" in tag.text):
        page_url = link['href']
        if "/locations-list" not in page_url:
            # print(page_url)

            r_loc = requests.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, 'lxml')
            locator_domain = base_url
            location_type = "<MISSING>"
            store_number = "<MISSING>"
            try:
                script = soup_loc.find(
                    'script', {'type': 'application/ld+json'}).text
                json_data = json.loads(script)
                location_name = json_data['name'].replace('&#39;', '`').strip()
                street_address = json_data['address']['streetAddress']
                city = json_data['address']['addressLocality']
                state = json_data['address']['addressRegion']
                zipp = json_data['address']['postalCode']
                country_code = json_data['address']['addressCountry']
                phone = json_data['telephone']
                latitude = json_data['geo']['latitude']
                longitude = json_data['geo']['longitude']
                hours_of_operation = " ".join(list(soup_loc.find(
                    'div', {'id': 'home-hours'}).stripped_strings)).strip().replace('Hours of Business','')

            except:
                continue
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(
                hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url)
            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if type(x) == str else x for x in store]
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
