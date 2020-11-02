import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "extra_hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://pontillospizza.com/menuslocations/ "
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.findAll('div', {'class', 'information'})
    if exists:
        for data in soup.findAll('div', {'class', 'information'}):
            if data.find('div', {'class', 'title'}):
                location_name = data.find('div', {'class', 'title'}).get_text()
            else:
                location_name = '<MISSING>'
            if data.find('div', {'class', 'address'}):
                address = data.find('div', {'class', 'address'}).get_text().strip().replace('\r\n', ' ')
                street_city_st_pin = address.split(' ')
                if street_city_st_pin[-1].isdigit():
                    street_address = ' '.join(street_city_st_pin[:-3])
                    city = street_city_st_pin[-3][:-1]
                    state = street_city_st_pin[-2]
                    zip = street_city_st_pin[-1]
                else:
                    street_address = ' '.join(street_city_st_pin[:-2])
                    city = street_city_st_pin[-2][:-1]
                    state = street_city_st_pin[-1]
                    zip = '<MISSING>'
            else:
                street_address = '<MISSING>'
                state = '<MISSING>'
                city = '<MISSING>'
                zip = '<MISSING>'

            if data.find('div', {'class', 'phone'}):
                phone = data.find('div', {'class', 'phone'}).get_text().strip()
            else:
                phone = '<MISSING>'

            if data.find_next('div', {'class', 'schedule'}):
                if data.find_next('div', {'class', 'schedule'}).find('div', {'class', 'delivery'}):
                    hours_of_operation = ' '.join(data.find_next('div', {'class', 'schedule'}).find('div', {'class', 'delivery'}).get_text().replace('\n', ' ').replace('\n\n', '').strip().split(' ')[2:])
                    extra_hours_of_operation = ' '.join(data.find_next('div', {'class', 'schedule'}).find('div', {'class', 'carryout'}).get_text().replace('\n', ' ').replace('\n\n', '').strip().split(' ')[2:])
                else:
                    hours_of_operation = '<MISSING>'
                    if data.find_next('div', {'class', 'schedule'}).find('div', {'class','carryout'}):
                        extra_hours_of_operation = ''.join(data.find_next('div', {'class', 'schedule'}).find('div', {'class','carryout'}).get_text().replace('\n', ' ').replace('\n\n', '').strip().split(' ')[2:])
                    else:
                        extra_hours_of_operation = '<MISSING>'
            else:
                extra_hours_of_operation = '<MISSING>'
                hours_of_operation = '<MISSING>'

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Pontillo's Pizzeria")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append(hours_of_operation)
            store.append(extra_hours_of_operation)
            return_main_object.append(store)
        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
