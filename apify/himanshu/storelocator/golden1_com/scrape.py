import csv
import requests
from bs4 import BeautifulSoup
import re
import sgzip
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}
    return_main_object = []
    base_url = "https://www.golden1.com/"
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 10

    result_coords = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    data_len = 0
    coords = search.next_coord()
    while coords:
        # print("zip_code === " + str(coords))
        # print("ramiang zip =====" + str(search.current_zip))

        data  = "lat="+str(coords[0])+"&lng="+str(coords[1])+"&searchby=ESC%7CATMSF%7CCOOP%7CCUSC%7C&SearchKey=&rnd=1566557208502"
        # data = "address=11756&lat=40.7226698&lng=-73.51818329999998&searchby=ESC%7CATMSF%7CCOOP%7CCUSC%7C&rnd=1571729652978"
        location_url = 'https://golden1.locatorsearch.com/GetItems.aspx'
        r = requests.post(location_url, headers=header, data=data)

        soup = BeautifulSoup(r.text, "html.parser")
        data_len = len(soup.find_all('marker'))
        for idx, v in enumerate(soup.find_all('marker')):

            latitude = v['lat']
            longitude = v['lng']
            result_coords.append((latitude, longitude))
            locator_domain = base_url
            location_name = v.find('label').text.replace('<br>', '')
            street_address = v.find('add1').text.replace('<br>', '')
            vk = v.find('add2').text.split(',')
            city = ''
            state = ''
            zip = ''
            city = vk[0].strip()
            if len(vk[1].strip().split(' ')) == 2:

                state = vk[1].strip().split(' ')[0].replace('HI','')
                if '<br><b>' in state:
                    state = ''
                if 'Restricted' in state:
                    state = ''
                zip = vk[1].strip().split(' ')[1]
                if 'Access</b>' in zip:
                    zip = ''
                if '-' in zip:
                    zip = ''

            country_code = 'USA'
            store_number = '<MISSING>'
            phone = '<MISSING>'
            location_type = '<MISSING>'
            hours_of_operation = ''
            get_hour  = BeautifulSoup(v.find('contents').text, "lxml").find('table')
            if get_hour != None:
                hours_of_operation = BeautifulSoup(v.find('contents').text, "lxml").find('table').text

            page_url = base_url
            if street_address in addresses:
                continue
            addresses.append(street_address)
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip if zip else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')

            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            print("data====", str(store))
            yield store
        if data_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif data_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
