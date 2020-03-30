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
    locator_domain = "https://countrycookin.com/"
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



    r= session.get('https://countrycookin.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    info = soup.find('div',class_='container-search-filter').find('div',class_='acf-map')
    for loc in info.find_all('div',class_='marker'):
        latitude = loc['data-lat']
        longitude = loc['data-lng']
        location_name = loc.h4.text.strip()
        address = loc.p
        add_list = list(address.stripped_strings)
        street_address = add_list[0].strip()
        city = add_list[1].split(',')[0]
        state = add_list[1].split(',')[1].split()[0]
        zipp = add_list[1].split(',')[1].split()[-1]
        phone = add_list[-1]
        # print(phone)
        hours= list(loc.stripped_strings)
        # print(hours)
        h = hours[4:-3]
        p = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(h[0]))
        if p != []:
           if "("+p[0] == h[0]:
                h.remove(h[0])
        hours_of_operation = " ".join(h).replace('Direction','').replace('&','and')
        slug =location_name.lower().replace(' ','-')
        page_url = "https://countrycookin.com/locations/" + slug





        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" or x == None  else x.encode('ascii', 'ignore').decode('ascii').strip() for x in store]

        print("data = " + str(store))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)



    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
