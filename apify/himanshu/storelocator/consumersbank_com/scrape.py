from sgrequests import SgRequests
import csv
from bs4 import BeautifulSoup
import re
import json


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.consumersbank.com"


    return_main_object = []

    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "consumersbank"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    r = session.get(
        "https://www.consumersbank.com/about-us/contact/locations-hours.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())
    for li in soup.find_all('li',class_="loc"):
        location_name = li['data-title']
        street_address = li['data-address1'] + " " + li['data-address2']
        city =li['data-city']
        state = li['data-state']
        zipp = li['data-zip']
        latitude = li['data-latitude']
        longitude = li['data-longitude']
        phone = li.find('span',class_="value").text.strip()
        hours= li.find('div',class_='hours')
        list_hours = list(hours.stripped_strings)
        if list_hours != []:
            hours_of_operation = " ".join(list_hours)
        else:
            hours_of_operation = "<MISSING>"
        page_url = base_url + li.find('a',class_='seeDetails')['href']
        store_number = page_url.split('?')[-1].split('=')[1].split('&')[0]

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

        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        print("data = " + str(store))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)
    return return_main_object





def scrape():
    data = fetch_data()
    write_output(data)


scrape()
