import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('caasco_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    store_detail = []
    
    lat = []
    lng=[]
    return_main_object = []
    address1 = []
    get_url ='https://www.caasco.com/store-locator'
    domain_url = 'https://www.caasco.com/'
    

    r = session.get(get_url, headers=headers)    
    soup = BeautifulSoup(r.text, "lxml")    
    # logger.info(soup)
    main =soup.find("input", {'id': 'locations'})['value']

    json_obj = json.loads(main)
    for i in json_obj:
        location_name =i['name']
        address = i['address']
        city =i['city']
        state= 'ON'
        zip=i['postal']
        phone= i['phone']
        lat= i['lat']
        lng=i['lng']
        hour= 'Monday' +' '+i['hours1']+' '+'Tuesday' +' '+i['hours2']+' '+'Wednesday' +' '+i['hours3']+' '+'Thursday' +' '+i['hours4']+' '+'Friday' +' '+i['hours5']+' '+'Saturday' +' '+i['hours6']+' '+'Sunday' +' '+i['hours7']       
        store=[]       
        store.append(domain_url)
        store.append(location_name)
        store.append(address)
        store.append(city)
        store.append(state) 
        store.append(zip)
        store.append('CA')
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hour)
        store.append("https://www.caasco.com" + i["moreInfo"])
        return_main_object.append(store)
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
           
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
