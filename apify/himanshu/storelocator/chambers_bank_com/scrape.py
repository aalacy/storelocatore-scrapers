import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from json import loads
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chambers_bank_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.chambers.bank/"
    r = session.get(base_url+'locations/',headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    name1 = []
    lat = []
    lng = []
    latitude =[]
    longitude =[]
    loc = session.get("https://www.chambers.bank/ajax/locations",headers = header).json()
    for i in loc:
        # logger.info(i)
        if not i['name']:
            pass
        else:
            lat.append(i['lat'])
            lng.append(i['lng'])
            # logger.info(i["phone"])
            name1.append(i["phone"])


    # logger.info(len(lat))
    db =  soup.find_all('div',{'class':'location'})
    for index,val in enumerate(db):
        # logger.info(index)
        locator_domain = base_url
        location_name = val.find_previous('h3').text.strip()
        street_address = val.find('p',{'class':'address'}).text.split('\n')[0].strip()
        city =  val.find('p',{'class':'address'}).text.split('\n')[1].strip().split(',')[0].strip().replace('AR 72837','').strip()

        if len(val.find('p',{'class':'address'}).text.split('\n')[1].strip().split(',')) >1:
            state = val.find('p',{'class':'address'}).text.split('\n')[1].strip().split(',')[1].split()[0].strip()
        else:
            state = val.find('p',{'class':'address'}).text.split('\n')[1].strip().split(',')[0].split()[-2].strip()
        zip = (val.find('p',{'class':'address'}).text.split('\n')[1].strip().split(",")[-1].split( )[-1].replace("AR","<MISSING>"))
        # logger.info(city +" | "+state+" | "+zip)
        store_number = '<MISSING>'
        phone = val.find('p',{'class':'address'}).find_next('p').text.replace('Phone:','').strip()
        country_code = 'US'
        location_type = '<MISSING>'
        # latitude = ''
        # longitude = ''

        for i in range(len(name1)):
            if name1[i]==phone:
                # logger.info(street_address)
                latitude.append(lat[index])
                longitude.append(lng[index])

        hours_of_operation = val.find_all('div',{'class':'hours-row'})
        bn = []
        for target_list in hours_of_operation:
            bn.append(target_list.text.strip())
        hours_of_operation = ''.join(bn).replace('\r','').replace('\n','')
        page_url = base_url+'locations/'

        store=[]
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
        store.append(latitude[index] if latitude[index] else '<MISSING>')
        store.append(longitude[index] if longitude[index]  else '<MISSING>')

        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        store.append(page_url  if page_url else '<MISSING>')
        if "1900 East Oak Street" in store:
            store[10]="35.0914721"
            store[11]="-92.4007896"
            # logger.info(store)
        return_main_object.append(store)
    # logger.info(len(latitude))
    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)

scrape()
