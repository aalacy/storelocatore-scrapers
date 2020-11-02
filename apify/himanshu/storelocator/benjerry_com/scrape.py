import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('benjerry_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.benjerry.com/ice-cream-near-me?tab=shop"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('div', {'class', 'bjnt_shopsList'})
    if exists:
        location_exists = ''
        for values in exists.findAll('span', {'class', 'h5span-genericText'}):
            if values.find('a'):
                if location_exists == values.find('a').get_text():
                    pass
                elif location_exists == '':
                    location_name = values.find('a').get_text()
                    location_exists = location_name
                    logger.info(location_name)
                    if "Dulles" in location_name:
                        street_address = values.find_next('span').get_text()
                        city_st_pin = values.find_next('span').find_next('span').get_text().strip().split(',')
                        city = city_st_pin[0]
                        if len(city_st_pin[1].strip().split(' ')) == 2:
                            state = city_st_pin[1].strip().split(' ')[0]
                            zip = city_st_pin[1].strip().split(' ')[1]
                        else:
                            state = "<MISSING>"
                            zip = "<MISSING>"
                        phone = values.find_next('span').find_next('span').find_next('span').get_text()
                    else:
                        if len(values.find_next('span').find_next('span').get_text()) > 5 and values.find_next('span').find_next('span').get_text()[-5].isdigit():
                            street_address = values.find_next('span').get_text()
                            city_st_pin = values.find_next('span').find_next('span').get_text().strip().split(',')
                            city = city_st_pin[0]
                            if len(city_st_pin[1].strip().split(' ')) == 2:
                                state = city_st_pin[1].strip().split(' ')[0]
                                zip = city_st_pin[1].strip().split(' ')[1]
                            else:
                                state = "<MISSING>"
                                zip = "<MISSING>"
                                if "n/a" in values.find_next('span').find_next('span').find_next('span').get_text():
                                    phone = "<MISSING>"
                                else:
                                    phone = values.find_next('span').find_next('span').find_next('span').get_text()
                        else:
                            street_address = values.find_next('span').get_text() + ", " + values.find_next('span').find_next('span').get_text()
                            city_st_pin = values.find_next('span').find_next('span').find_next('span').get_text().strip().split(',')
                            city = city_st_pin[0]
                            if len(city_st_pin[1].strip().split(' ')) == 2:
                                state = city_st_pin[1].strip().split(' ')[0]
                                zip = city_st_pin[1].strip().split(' ')[1]
                            else:
                                state = "<MISSING>"
                                zip = "<MISSING>"
                            phone = values.find_next('span').find_next('span').find_next('span').find_next('span').get_text()
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
                    store.append("Chili's Grill & Bar - Local Restaurants Near Me | Chili's")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    return_main_object.append(store)
                else:
                    location_name = values.find('a').get_text()
                    location_exists = location_name
                    logger.info(location_name)
                    if "Dulles" in location_name:
                        street_address = values.find_next('span').get_text()
                        city_st_pin = values.find_next('span').find_next('span').get_text().strip().split(',')
                        city = city_st_pin[0]
                        if len(city_st_pin[1].strip().split(' ')) == 2:
                            state = city_st_pin[1].strip().split(' ')[0]
                            zip = city_st_pin[1].strip().split(' ')[1]
                        else:
                            state = "<MISSING>"
                            zip = "<MISSING>"
                        phone = values.find_next('span').find_next('span').find_next('span').get_text()
                    else:
                        if len(values.find_next('span').find_next('span').get_text()) > 5 and \
                                values.find_next('span').find_next('span').get_text()[-5].isdigit():
                            street_address = values.find_next('span').get_text()
                            city_st_pin = values.find_next('span').find_next('span').get_text().strip().split(',')
                            city = city_st_pin[0]
                            if len(city_st_pin[1].strip().split(' ')) == 2:
                                state = city_st_pin[1].strip().split(' ')[0]
                                zip = city_st_pin[1].strip().split(' ')[1]
                            else:
                                state = "<MISSING>"
                                zip = "<MISSING>"
                                if "n/a" in values.find_next('span').find_next('span').find_next('span').get_text():
                                    phone = "<MISSING>"
                                else:
                                    phone = values.find_next('span').find_next('span').find_next('span').get_text()
                        else:
                            street_address = values.find_next('span').get_text() + ", " + values.find_next(
                                'span').find_next('span').get_text()
                            city_st_pin = values.find_next('span').find_next('span').find_next(
                                'span').get_text().strip().split(',')
                            city = city_st_pin[0]
                            if len(city_st_pin[1].strip().split(' ')) == 2:
                                state = city_st_pin[1].strip().split(' ')[0]
                                zip = city_st_pin[1].strip().split(' ')[1]
                            else:
                                state = "<MISSING>"
                                zip = "<MISSING>"
                            phone = values.find_next('span').find_next('span').find_next('span').find_next(
                                'span').get_text()
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
                    store.append("Chili's Grill & Bar - Local Restaurants Near Me | Chili's")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    return_main_object.append(store)
        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)
scrape()