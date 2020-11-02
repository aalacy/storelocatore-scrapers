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
    base_url = "https://interstatebatteries.com"
    r = session.get(base_url+"/all-battery-center-locations")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main = soup.find('div',{'class':"store-directory"}).find('ul',{"class":"list"}).find_all('a')
    for dt in main:
        if re.search('/locations/',dt['href']):
            r1 = session.get(base_url+dt['href'])
            soup1 = BeautifulSoup(r1.text,"lxml")
            if "Sorry, but the page you are looking for can't be found." not in soup1.text:
                country=""
                for script in soup1.find_all('script'):
                    if "localstoreinfo" in script.text:
                        country=json.loads(script.text.split('localstoreinfo = ')[1].replace(";",''))['Country']
                if soup1.find('div',{"id":"couponModal"})!=None:
                    adr=soup1.find('div',{"id":"couponModal"}).find('input',{"name":"locationAddress1"})['value'].strip()
                    city=soup1.find('div',{"id":"couponModal"}).find('input',{"name":"locationCity"})['value'].strip()
                    state=soup1.find('div',{"id":"couponModal"}).find('input',{"name":"locationState"})['value'].strip()
                    zip=soup1.find('div',{"id":"couponModal"}).find('input',{"name":"locationPostalCode"})['value'].strip()
                    phone=soup1.find('div',{"id":"couponModal"}).find('input',{"name":"locationPhone"})['value'].strip()
                    hour=list(soup1.find('div',{"class":"store-hours"}).stripped_strings)
                    del hour[0]
                    store=[]
                    store.append("https://interstatebatteries.com")
                    store.append(soup1.find('ol',{"class":"breadcrumb"}).find('a',{"href":dt['href']}).text.strip())
                    store.append(adr)
                    store.append(city)
                    store.append(state)
                    store.append(zip)
                    if country=="USA":
                        if len(zip.replace(' ',''))==6:
                            store.append('CA')
                        else:
                            store.append('US')
                    elif country=="CAN":
                        store.append('CA')
                    elif country:
                        store.append(country)
                    else:
                        store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append("interstatebatteries")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(" ".join(hour))
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
