import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('topstarexpress_com')


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

    locator_domain = "https://www.topstarexpress.com/"
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


    url = "https://www.topstarexpress.com/wp-admin/admin-ajax.php"

    querystring = {"action":"get_stores","lat":"","lng":"","radius":"10000000000","categories[0]":""}

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\nget_stores\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"lat\"\r\n\r\n40.7998227\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"lng\"\r\n\r\n-73.65096219999998\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"radius\"\r\n\r\n1000\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"categories%5B0%5D\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'accept': "text/html, */*; q=0.01",
        'cache-control': "no-cache",
        'postman-token': "a1d955b6-8ac9-15bc-edf1-4dbed597f8ae"
        }

    response = session.post( url, data=payload, headers=headers, params=querystring)

    json_data = response.json()
    for loc in json_data:
        store_number = json_data[loc]['ID'].strip()
        location_name = json_data[loc]['na'].strip()
        page_url = json_data[loc]['gu'].strip()
        latitude = json_data[loc]['lat'].strip()
        longitude = json_data[loc]['lng'].strip()
        street_address = json_data[loc]['st'].strip()
        city = json_data[loc]['ct'].strip()
        zipp = json_data[loc]['zp'].strip()
        phone= json_data[loc]['te'].strip()
        try:
            r1 = session.get(page_url)
            soup_r1 = BeautifulSoup(r1.text,'lxml')
            address = soup_r1.find('div',class_='store_locator_single_address')
            list_address= list(address.stripped_strings)
            state= list_address[-1].split(',')[-1].split()[0].strip()
            hours = soup_r1.find('div',class_='store_locator_single_opening_hours')
            if  hours !=None:
                list_hours = list(hours.stripped_strings)
                hours_of_operation = " ".join(list_hours).strip()
            else:
                hours_of_operation = "<MISSING>"
        except:
            #logger.info(page_url)
            #logger.info('******************************************************')
            continue
        # result_coords.append((latitude, longitude))
        if street_address in addresses:
            continue
        addresses.append(street_address)
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
        store.append(hours_of_operation.replace("Opening Hours",'') if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # logger.info("data===="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store





def scrape():
    data = fetch_data()
    write_output(data)


scrape()
