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
    base_url = "https://www.urgentteam.com"
    return_main_object=[]
    r = session.get(base_url+"/location-map-page")
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{'class':'view-content'}).find_all('div',{"class":"views-row"})
    for loc in main:
        name=loc.find('h2',{"class":"location-title"}).find('a').text.strip()
        address=loc.find('div',{'class':"thoroughfare"}).text.strip()
        city=loc.find('span',{'class':"locality"}).text.strip()
        state=loc.find('span',{'class':"state"}).text.strip()
        country=loc.find('span',{'class':"country"}).text.strip()
        if country=="United States":
            country="US"
        zip=loc.find('span',{'class':"postal-code"}).text.strip()
        phone=loc.find('div',{'class':"location-phone"}).find('div',{"class":"field-content"}).find('a').text.strip()
        lt=loc.find('div',{'class':"location-directions"}).find('a')['href'].split('@')
        lat=''
        lng=''
        if len(lt)>1:
            lat=lt[1].split(',')[0]
            lng=lt[1].split(',')[1]
        hour=''
        if loc.find('div',{'class':"location-hours"})!=None:
            hour=' '.join(list(loc.find('div',{'class':"location-hours"}).find('div',{"class":"field-content"}).stripped_strings))
        storeno=''
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("urgentteam")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
