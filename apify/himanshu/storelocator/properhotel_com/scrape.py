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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.properhotel.com"
    return_main_object=[]
    r = session.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    
    for dt in soup.find("li",{"class":"menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-551"}).find('ul',{"class":'sub-menu'}).find_all('a'):
       
        r1 = session.get(dt['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        city=dt.text.strip()
        main1=soup1.find('div',{"class":'ftr-address'})
        if soup1.find('div',{"class":'ftr-address'})!=None:
            loc=list(main1.stripped_strings)[1].split(',')
            storeno=''
            lt=main1.find('a',alt="Map Marker")['href'].split('@')[1].split(',')
            country="US"
            address=loc[0].replace(city,'').split('(')[0].strip()
            address=re.sub(r'\s+',' ',address)
            state=loc[-1].strip().split(' ')[0].strip()
            zipp=loc[-1].strip().split(' ')[1].strip()
            lat=lt[0]
            lng=lt[1]
            
            
            phone = list(soup1.find('div',{"class":'ftr-phone'}).stripped_strings)[-1]
            if phone.replace("-","").isdigit():
                phone = phone
            else:
                phone = "<MISSING>"
            data8 = city.lower().replace(" ","-").replace(".","")
            page_url = "https://www.properhotel.com/hotels/"+str(data8)
            store=[]
            store.append(base_url)
            store.append(city if city else "<MISSING>")
            store.append(address.replace("Entrance at ",'') if address else "<MISSING>")
            store.append(city.replace("Downtown L.A.",'Los Angeles') if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append(storeno if storeno else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append("<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
