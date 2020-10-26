import csv
from sgrequests import SgRequests
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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    return_main_object = []
    base_url = "http://fayettepartsservice.com"
    r = session.get(
        "http://fayettepartsservice.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all('a', {'title': 'View Location Details'}):
        page_url = link['href']
        store_number = page_url.split('-')[-1].strip()
        country_code = "US"
        location_type = "<MISSING>"
        locator_domain = base_url
        r_loc = session.get(page_url, headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, 'lxml')

        try:
            address = list(soup_loc.find(
                'div', {'id': 'address'}).stripped_strings)
            if "Address:" in " ".join(address):
                address.remove("Address:")
            street_address = " ".join(address[:-1]).strip()
            city = address[-1].split(',')[0].strip()
            state = address[-1].split(',')[1].split()[0].strip()
            zipp = address[-1].split(',')[1].split()[-1].strip()
            phone = list(soup_loc.find('div', {'id': 'address'}).find_next(
                'p').stripped_strings)[0]
            hours_of_operation = " ".join(list(soup_loc.find(
                lambda tag: (tag.name == "b") and "Hours:" == tag.text.strip()).parent.stripped_strings)).replace("Hours:", "").strip()
            coords = soup_loc.find(lambda tag: (
                tag.name == "script") and "var map;" in tag.text.strip())

            latitude = coords.text.split('.LatLng(')[
                1].split(');')[0].split(',')[0].strip()
            longitude = coords.text.split('.LatLng(')[
                1].split(');')[0].split(',')[-1].strip()
            location_name = city + "," + state
            # print(latitude, longitude)
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        except:
            pass
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        store = ["<MISSING>" if x == "" else x for x in store]
        # print("data ==" + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
