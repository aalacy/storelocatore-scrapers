import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    locator_domain = base_url = "https://www.nanticoke.org/"

    r = session.get("https://www.nanticoke.org/locations/")
    soup = BeautifulSoup(r.text, "lxml")
    json_data = json.loads(soup.find(lambda tag: (tag.name == "script" ) and "var gmpAllMapsInfo =" in tag.text.strip()).text.split("var gmpAllMapsInfo = ")[1].replace("}];",'}]').replace("/* ]]> */",''))

    kk = []
    jk = {}
    for x in json_data:
        for x in x['markers']:
            jk[x['title']] = [x['coord_x'],x['coord_y']]
            kk.append(jk)

    for x in soup.find('div',{'class':'locations'}).find_all('div',{'class':'col-sm-4'}):

        location_name = x.find('h3').text.strip()

        main_address = x.find('p').text.split('\n')
        if len(main_address) == 4:
            del main_address[0]
        street_address = main_address[0].strip()
        city = main_address[1].split(',')[0].strip()
        state = main_address[1].split(',')[1].strip().split(' ')[0]
        zipp = main_address[1].split(',')[1].strip().split(' ')[1]
        phone = x.find('a',{'class':'mobile'}).text
        latitude = '<MISSING>'
        longitude = '<MISSING>'

        if location_name in kk[0].keys():
            latitude = kk[0][location_name][0]
            longitude =  kk[1][location_name][1]
        country_code = "US"
        store_number = '<MISSING>'

        location_type = '<MISSING>'
        hours_of_operation = '<MISSING>'
        page_url = base_url
        street_address = street_address.lower().replace('suite', '').replace('floor', '').capitalize()
        store = [locator_domain, location_name.replace('\n', ' ').replace(', unit 101',''), street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [str(x).strip() if x else "<MISSING>" for x in store]

        yield store

    for x in soup.find('div',{'class':'locations'}).find_all('div',{'class':'col-sm-6'}):

        if x.find('h3'):
            location_name = x.find('h3').text.strip()

            main_address = x.find('p').find_next('p').text.split('\n')
            if len(main_address) == 3:
                del main_address[0]

            street_address = main_address[0].strip()
            city = main_address[1].split(',')[0].strip()
            state = main_address[1].split(',')[1].strip().split(' ')[0]
            zipp = main_address[1].split(',')[1].strip().split(' ')[1]
            phone = x.find('a', {'class': 'mobile'}).text

            latitude = '<MISSING>'
            longitude = '<MISSING>'
            if location_name in kk[0].keys():
                latitude = kk[0][location_name][0]
                longitude = kk[1][location_name][1]
            country_code = "US"
            store_number = '<MISSING>'

            location_type = '<MISSING>'
            hours_of_operation = '<MISSING>'
            page_url = base_url
            if "Suite" in street_address or "Floor" in street_address:
                street_address = street_address.split('Suite')[0].split('Floor')[0].replace(',','')
            mm = []

            while custome_demo(',',street_address):

                mm.append(street_address.split(',')[0])
                street_address = street_address.split(',')[0]

            if len(mm) != 0:
                street_address = mm[-1]


            store = [locator_domain, location_name, street_address.replace(', unit 101',''), city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = [str(x).strip().replace('\n', ' ') if x else "<MISSING>" for x in store]

            yield store


def custome_demo(ticker,name):

    if (name.find(',') != -1):
        return True
    else:
        return False
def scrape():
    data = fetch_data()
    write_output(data)

scrape()



