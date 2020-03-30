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
    base_url = "https://www.legalseafoods.com"
    r = session.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('select',{"id":"restaurantDetailURL"}).find_all("option")
    del main[0]
    for link in main:
        r1 = session.get(base_url+link['value'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('div',{"class":'Detail Body'})
        name=main1.find('h4').text.strip()
        address=main1.find('address',{"class":"Address"}).find('span',{"class":"street1 Property"}).text.strip()        
        city=main1.find('address',{"class":"Address"}).find('span',{"class":"city Property"}).text.strip()
        state=main1.find('address',{"class":"Address"}).find('span',{"class":"subcountry Property"}).text.strip()
        zip=main1.find('address',{"class":"Address"}).find('span',{"class":"postal Property"}).text.strip()
        phone=main1.find('a',{"class":"Phone"}).text.strip()
        hour=""
        if main1.find('table') != None:
            hour=' '.join(main1.find('table').stripped_strings).strip()  
        store=[]
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("legalseafoods")
        store.append("<MISSING>")
        store.append("<MISSING>")
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
