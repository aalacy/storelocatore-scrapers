import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://mymotomart.com"

    soup = BeautifulSoup(session.get(base_url+"/Locations").text,'lxml')
   
    main=soup.find('div',{"id":"dnn_RightPane"}).find_all('div',{"class":"highrow"})
    for loc in main:
        name=loc.find('div',{"class":"storeNames"}).text.strip()
        if loc.find('div',{"class":"storeAddress"})!=None:
            madd=list(loc.find('div',{"class":"storeAddress"}).stripped_strings)
        else:
            madd=list(loc.find('div',{"class":"storAddress"}).stripped_strings)
        address = " ".join(madd[:-2])

        city = madd[-2].split(",")[0].strip()
        state = madd[-2].split(",")[1].split()[0].strip()
        zipp = madd[-2].split(",")[1].split()[1].strip()
        phone = madd[-1].strip()

        lat = loc.find("button", {"onclick": re.compile("&lat=")})['onclick'].split('lat=')[1].split('&')[0].strip()
        lng = loc.find("button", {"onclick": re.compile("&lat=")})['onclick'].split('lon=')[1].split('&')[0].strip()
    
        country="US"
        hour=''
       
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append("<MISSING>")
        
        yield store
 

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
