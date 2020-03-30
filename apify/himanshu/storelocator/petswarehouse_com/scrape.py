import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

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
    # zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    base_url =  "https://www.petswarehouse.com/"
    locator_domain = "https://www.petswarehouse.com/"
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
    page_url = ''
    r = session.get('https://app.mapply.net/front-end/iframe.php?api_key=mapply.ef0d3ad63fbf8f5a3a082ddb25888456')
    soup = BeautifulSoup(r.text,'lxml')
    c1= []
    c2  = []
    coords = soup.find('div',class_='header_html').find_previous('script').text.strip().split('markersCoords.push')
    for ll in coords[1:6]:
        lat= ll.split('({')[1].split(',')[0].split(':')[1].strip()
        lng = ll.split('({')[1].split(',')[1].split(':')[1].strip()
        # print(lat,lng)
        c1.append(lat)
        c2.append(lng)
    address = soup.find('div',{'id':'addresses_list'}).find('ul')
    for li in address.find_all('li'):
        store_number = li.find('a')['onclick'].split('(')[-1].split(')')[0].strip()
        location_name = li.find('span',class_='name').text.strip()
        street_address = li.find('span',class_='address').text.strip() + " " + li.find('span',class_='address2').text.strip()
        city = li.find('span',class_='city').text.strip()
        state = li.find('span',class_='prov_state').text.strip()
        zipp = li.find('span',class_='postal_zip').text.strip()
        phone_tag = li.find('span',class_='phone').text.strip()
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
        if phone_tag != []:
            phone = phone_list[0]
        else:
            phone = "<MISSING>"
        hours_of_operation = li.find('span',class_="hours").text.strip()
        if c1 != []:
            latitude = c1.pop(0)
            longitude = c2.pop(0)
        else:
            pass
        page_url = "https://www.petswarehouse.com/store-locator/"


        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [x if x.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" for x in store]

        if store[2] in addresses:
            continue
        addresses.append(store[2])

        #print("data = " + str(store))
        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)






    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
