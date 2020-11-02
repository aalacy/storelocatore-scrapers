import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mycfe_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.additionfi.com/"
    location_url  = 'https://www.additionfi.com/RestApi/locations?type=Branches&format=json'
    r = session.get(location_url ,headers = header).json()


    for idx, val in enumerate(r['Locations']):

        locator_domain = base_url
        location_name = val['Title']
        street_address = val['Address']['Street'].strip()

        city = val['Address']['City'].strip()
        state = val['Address']['StateCode'].strip()
        zip = val['Address']['Zip'].strip()

        store_number = '<MISSING>'
        country_code = 'US'
        phone = val['Phone']
        location_type = 'additionfi'
        latitude = val['Address']['Latitude']
        longitude = val['Address']['Longitude']
        r = session.get(base_url+'locations-hours/detail/'+val['UrlName'],headers = header)
        # logger.info(base_url+'locations-hours/detail/'+val['UrlName'])
        # exit()
        soup = BeautifulSoup(r.text,"lxml")

        hours_of_operation = soup.find('div',{'class':'hours-spreadsheet'}).find_all('div',{'class':'hours-row'})

        cc= []
        for vv in hours_of_operation:

            cc.append(vv.find('div',{'class':'days'}).text+vv.find_all('div',{'class':'times'})[0].text+vv.find_all('div',{'class':'times'})[1].text)


        hours_of_operation = 'Lobby - Drive-up :'+''.join(cc).strip()
        hours_of_operation = re.sub(r'\s+',' ',hours_of_operation).replace('N/A','-')



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
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')

        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        logger.info("====",str(store))

        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)

scrape()
