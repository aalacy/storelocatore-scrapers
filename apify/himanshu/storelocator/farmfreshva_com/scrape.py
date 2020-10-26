import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('farmfreshva_com')




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
    base_url = "https://www.farmfreshva.com"
    get_url ='https://www.farmfreshva.com'
    r = session.get(get_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")    
    main = soup.find_all('div',{'class':'et_pb_blurb_container'})[:2]
    for i in main:
        st = list(i.stripped_strings)
        location_name = st[0]
        address =st[1]
        city_tmp= st[2].split(',')
        city = city_tmp[0]
        state = city_tmp[1]
        zip = city_tmp[2]
        phone = st[3]     

        store=[]
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(address if address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append('US')
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        return_main_object.append(store)
        #logger.info("data ==== "+str(store))
    return return_main_object
        
def scrape():
    data = fetch_data()    
    write_output(data)

scrape()
