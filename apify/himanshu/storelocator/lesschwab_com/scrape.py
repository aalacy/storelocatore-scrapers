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
    base_url = "https://www.lesschwab.com"
    r = session.get(base_url+"/stores/")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"class":'footer__container__item'}).find_all('a')
    for atag in main:
        r1 = session.get(atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('div',{"class":'storeSearch__resultsSection'}).find('div',{"class":"render"})
        for location in json.loads(main1['data-json'],strict=False)['storeList']:
            store=[]
            cleanr = re.compile('<.*?>')
            hour = re.sub(cleanr, ' ', location['hours'])
            hour=re.sub(r'\s+', ' ', hour).strip()
            store.append(base_url)
            store.append(location['title'])
            store.append(location['address1'])
            store.append(location['city'])
            store.append(location['stateCode'])
            store.append(location['postalCode'])
            store.append("US")
            store.append(location['appointmentCTA']['storeId'])
            if location['phone']:
                store.append(location['phone'])
            else:
                store.append("<MISSING>")
            store.append("lesschwab")
            store.append(location['latitude'])
            store.append(location['longitude'])
            if hour:
                store.append(hour)
            else:
                store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
