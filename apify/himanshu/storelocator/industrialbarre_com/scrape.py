import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    return_main_object = []
    


    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data
    base_url = 'https://industrialbarre.com/'
    locator_domain = "https://industrialbarre.com/"
    page_url = "<MISSING>"
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

    r = session.get('https://industrialbarre.com/studios',headers = headers)
    soup= BeautifulSoup(r.text,'lxml')
    # print(soup.prettify())
    ph = []
    for phone_tag in soup.find_all('div',class_='col sqs-col-6 span-6')[0:2]:
        list_phone = list(phone_tag.stripped_strings)
        ph.append(list_phone[1].strip())


    for info in soup.find_all('div',class_='sqs-block-map'):
        data_to_fetch= info['data-block-json']
        json_data = json.loads(data_to_fetch)
        location_name =json_data['location']['addressTitle']
        latitude = json_data['location']['mapLat']
        longitude = json_data['location']['mapLng']
        street_address = json_data['location']['addressLine1']
        city = json_data['location']['addressLine2'].split(',')[0].strip()
        state = json_data['location']['addressLine2'].split(',')[1].strip()
        zipp = json_data['location']['addressLine2'].split(',')[-1].strip()
        phone= ph.pop(0)
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" or x == None else x for x in store]
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)
    return return_main_object



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
