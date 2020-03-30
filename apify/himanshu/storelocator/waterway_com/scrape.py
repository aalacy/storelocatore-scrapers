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
    base_url = "https://www.waterway.com"
    r = session.get(base_url+"/locations/")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    output=[]
    main=soup.find_all('div',{"class":'location-box'})
    for atag in main:
        name=atag.find('h3').text.strip()
        madd=list(atag.find('div',{"class":'location-info'}).stripped_strings)
        address=madd[0].strip()
        ct=madd[1].strip().split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        phone=madd[-1].strip()
        link=atag.find('a',{'class':"btn-link"})['href']
        r1 = session.get(link)
        soup1=BeautifulSoup(r1.text,'lxml')
        hour=''
        if soup1.find('table',{"class":"car-wash-hours"})!=None:
            main1=soup1.find('table',{"class":"car-wash-hours"})
            hour+=' '.join(list(main1.stripped_strings))+' , '
        if soup1.find('table',{"class":"gas-sta-hours"})!=None:
            main2=soup1.find('table',{"class":"gas-sta-hours"})
            hour+=' '.join(list(main2.stripped_strings))
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
        store.append("waterway")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hour if hour else "<MISSING>")
        if zip not in output:
            output.append(zip)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
