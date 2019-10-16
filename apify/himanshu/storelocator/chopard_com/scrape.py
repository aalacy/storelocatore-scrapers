import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time


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
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.chopard.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"



    r= requests.get('https://www.chopard.com/us/storelocator',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    script = soup.find_all('script',{'type':'text/javascript'})[-6]
    # script_text = '"stores":'+script.text.split('"stores":')[-1].split(']')[0]+']'
    script_text = script.text.split('=')[-1].split(';')[0]
    # print(script.text)
    # print(script_text)
    json_data = json.loads(script_text)
    # print(json_data['stores'])
    for x in json_data['stores']:
        page_url = x['details_url']
        store_number =x['store_code']
        location_name = x['name']
        if x['address_2'] ==None and x['address_3'] == None:
            street_address = x['address_1']
        elif x['address_2'] !=None and x['address_3'] == None:
            street_address = x['address_1'] + x['address_2']
        elif x['address_1'] !=None and x['address_2'] !=None and x['address_3'] !=None :
            street_address = x['address_1'] + x['address_2'] + x['address_3']
        city = x['city']
        zipp = x['zipcode']
        # print(zipp)
        latitude = x['lat']
        longitude = x['lng']
        phone = x['phone']
        country_code = x['country_id']
        # print(street_address)




        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" or x == None or x == "." else x for x in store]

        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)



    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
