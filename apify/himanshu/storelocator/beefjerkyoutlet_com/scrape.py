import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.beefjerkyoutlet.com"
    return_main_object=[]
    r = requests.get(base_url+'/location-finder')
    soup=BeautifulSoup(r.text,'lxml')
    output=[]
    main=soup.find('ul',{'class':'geolocation-common-map-locations'}).find_all('li')
    for ltag in main:
        lat=ltag['data-lat']
        name=ltag.find('span',{'class':'title'}).text.strip()
        lng=ltag['data-lng']
        link=ltag.find('a',text="Shop this store")['href']
        r1 = requests.get(base_url+link)
        soup1=BeautifulSoup(r1.text,'lxml')
        address=soup1.find('div',{'class':'views-field-field-address'}).find('span',{'class':'address-line1'}).text.strip()
        if soup1.find('div',{'class':'views-field-field-address'}).find('span',{'class':'address-line2'})!=None:
            address +=' '+soup1.find('div',{'class':'views-field-field-address'}).find('span',{'class':'address-line2'}).text.strip()
        address=address.replace('-',' ')
        city=soup1.find('div',{'class':'views-field-field-address'}).find('span',{'class':'locality'}).text.strip()
        state=soup1.find('div',{'class':'views-field-field-address'}).find('span',{'class':'administrative-area'}).text.strip()
        zip=soup1.find('div',{'class':'views-field-field-address'}).find('span',{'class':'postal-code'}).text.strip()
        country=soup1.find('div',{'class':'views-field-field-address'}).find('span',{'class':'country'}).text.strip()
        if country=="United States":
            country="US"
        try:
            hour=' '.join(soup1.find('div',{'class':'views-field-field-store-hours'}).find('div',{'class':'field-content'}).stripped_strings)
        except:
            hour=''
        phone=soup1.find('div',{'class':'views-field-field-store-phone'}).find('div',{'class':'field-content'}).text.strip()
        storeno=name.split('-')[-1].strip()
        store=[]
        store.append(base_url)
        store.append(name.encode('ascii', 'ignore').decode('ascii') if name else "<MISSING>")
        store.append(address.encode('ascii', 'ignore').decode('ascii') if address else "<MISSING>")
        store.append(city.encode('ascii', 'ignore').decode('ascii') if city else "<MISSING>")
        store.append(state.encode('ascii', 'ignore').decode('ascii') if state else "<MISSING>")
        store.append(zip.encode('ascii', 'ignore').decode('ascii') if zip else "<MISSING>")
        store.append(country.encode('ascii', 'ignore').decode('ascii') if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("beefjerkyoutlet")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour.encode('ascii', 'ignore').decode('ascii') if hour.strip() else "<MISSING>")
        if zip not in output:
            output.append(zip)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
