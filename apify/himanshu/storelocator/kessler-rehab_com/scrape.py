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
    base_url = "https://www.kessler-rehab.com/company/locations/Default.aspx"
    r = session.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('dl',{"class":"contact-info"})
    for atag in main:
        name=atag.find_parent('div').find_parent('div').find('h2').text
        loc=list(atag.stripped_strings)
        address=loc[1].strip()
        city=loc[2].split(',')[0].strip()
        state=loc[2].split(',')[1].strip().split(' ')[0]
        zip=loc[2].split(',')[1].strip().split(' ')[1]
        phone=loc[4]
        store=[]
        store.append("https://www.kessler-rehab.com")
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append('US')  
        store.append("<MISSING>")
        store.append(phone)
        store.append("Kessler Rehab")
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
