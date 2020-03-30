import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time



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
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = 'http://www.childrenslighthouse.com/'
    locator_domain = "http://www.childrenslighthouse.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    r_loc= session.get('https://childrenslighthouse.com/find-a-daycare')
    soup_loc= BeautifulSoup(r_loc.text,'lxml')
    select = soup_loc.find('select',class_='all_regions_list').find('option',{'value':'hoover-childcare-near-me'})

    s1 = base_url + select.text.lower().strip()+"Al"

    r1 = session.get(s1,headers=headers)
    soup = BeautifulSoup(r1.text,'lxml')
    info= soup.find('div',class_= "school_contact_information")
    list_info = list(info.stripped_strings)
    location_name = list_info[0]
    phone = list_info[1]
    street_address = list_info[3]
    city = list_info[-1].split(',')[0]
    state = list_info[-1].split(',')[-1].split()[0]
    zipp = list_info[-1].split(',')[-1].split()[-1]
    page_url = s1

    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
    store = ["<MISSING>" if x == "" else x for x in store]

    # print("data = " + str(store))
    # print(
    #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    return_main_object.append(store)


    r= session.post('https://childrenslighthouse.com/ajax/locations.php',headers = headers)
    json_data = r.json()

    for z in json_data:
        store_number = z['ID']
        location_name = z['name']
        street_address = z['address']
        city = z['city']
        state = z['state']
        zipp = z['zip']
        phone = z['phone']
        latitude = z['lat']
        longitude = z['lon']
        page_url = base_url + z['website']
        # print(city,state,zipp)




        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" else x for x in store]

        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
