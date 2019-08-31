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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.northernlightspizza.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.select('.col-xs-12.col-sm-6.col-sd-4.col-md-3.col-xl-4')
    if exists:
        for values in soup.select('.col-xs-12.col-sm-6.col-sd-4.col-md-3.col-xl-4'):
            if values.select('.listing__heading'):
                city = values.select('.listing__heading')[0].get_text()
            else:
                city = '<MISSING>'
            if values.select('.listing__detail'):
                location_name = values.select('.listing__detail')[0].get_text()
            else:
                pass
            if values.find('a'):
                phone = values.find('a').get_text()
            else:
                phone = '<MISSING>'

            StAndPin = values.select('.listing__contact')[0].select('.listing__detail')[1].get_text().strip()
            stAndPins = StAndPin.replace('\n', ' ').split(' ')
            if stAndPins[-1].isdigit():
                zip = stAndPins[-1]
                state = "Iowa"
            else:
                zip = '<MISSING>'
                state = "Iowa"
            street_address = stAndPins[0] + "," + (' ').join(stAndPins[1:])
            hours_val = values.select('.listing__hours')
            if hours_val:
                hours_of_operation = hours_val[0].select('.listing__detail')[0].get_text().replace('\n', ', ')[2:]
            else:
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
            store.append("Northern Lights Pizza Company® Your Home of the TastyCrust")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append(hours_of_operation)
            return_main_object.append(store)
        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()