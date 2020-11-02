import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
    base_url = "https://www.johnstonesupply.com/storefront/static/findAStore.ep"
    r = session.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('select',{"id":"selectStoreStates"}).find_all('option')
    for atag in main:
        link="https://www.johnstonesupply.com/storefront/findByStateOrZip.ep?state="+atag['value']+"&sortBy=undefined"
        r1 = session.get(link)
        soup1=BeautifulSoup(r1.text,'lxml')
        for val in soup1.find_all('div',{"class":"floatLeft width400"}):
            loc=list(val.stripped_strings)
            name=loc[0].strip()
            address=loc[1].strip()
            city=loc[2].split(',')[0].strip()
            state=loc[2].split(',')[1].strip().split(' ')[0]
            zip=loc[2].split(',')[1].strip().split(' ')[1]
            phone=loc[4]
            store=[]
            store.append("https://www.johnstonesupply.com")
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            if zip:
                store.append(zip)
            else:
                 store.append('<MISSING>')
            store.append('US')  
            store.append("#"+loc[0].split('#')[-1].strip())
            store.append(phone.replace('(HEAT)',''))
            store.append("johnstonesupply")
            store.append('<MISSING>')
            store.append('<MISSING>')
            store.append('<MISSING>')
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
