import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('enterprisetrucks_com')




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
    base_url = "https://www.enterprisetrucks.com"
    r = session.get(base_url+"/truckrental/en_US/locations.html")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main=soup.find("div",{"id":"locationsstatelisting"}).find_all("a")
    for atag in main:
        r1 = session.get(base_url+atag['href'])
        soup1 = BeautifulSoup(r1.text,"lxml")
        if 'Our apologies…an unexpected error occurred.' not in r1.text:
            try:
                address=soup1.find('form',{'id':'getDirectionForm'}).find('input',{"id":"addressLine"})['value'].strip()
            except Exception as e:
                logger.info(e)
            city=soup1.find('form',{'id':'getDirectionForm'}).find('input',{"id":"cityName"})['value'].strip()
            name=city+' Truck Rental'
            state=soup1.find('form',{'id':'getDirectionForm'}).find('input',{"id":"stateProvCode"})['value'].strip()
            zip=soup1.find('form',{'id':'getDirectionForm'}).find('input',{"id":"postalCode"})['value'].strip()
            country=soup1.find('form',{'id':'getDirectionForm'}).find('input',{"id":"coutryCode"})['value'].strip()
            phone=soup1.find('form',{'id':'locationDownloadForm'}).find('input',{"id":"location_phone"})['value'].strip()
            hr=soup1.find('table',{'class':"timing"}).find_all('tr')
            del hr[0]
            hours=""
            for hval in hr:
                hours+=' '.join(list(hval.stripped_strings))+"  "
            store=[]
            store.append("https://www.enterprisetrucks.com")
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append(country)  
            store.append("<MISSING>")
            store.append(phone)
            store.append("enterprisetrucks")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
