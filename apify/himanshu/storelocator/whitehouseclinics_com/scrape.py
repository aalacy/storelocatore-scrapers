import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" ,"page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    return_main_object=[]
    headers = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }
    base_url= "https://whitehouseclinics.com/locations-hours"
    r= session.get(base_url,headers=headers)
    soup=BeautifulSoup(r.text, "lxml")
    location_name=[]
    r_locations = soup.find_all("div",{"class":"fusion-text"})[1:]
    r_location_name= soup.find_all("h2",{"class":"title-heading-left"})
    for location in r_location_name:
        location_name.append(location.text)
    for index,location in enumerate(r_locations):
        store=[]
        data=(list(location.stripped_strings))
        hours_of_operation=data[0].replace("No services currently offered at this location.","<MISSING>")
        if  "Fax #:" in data[-1]:
            del data[-1]
        street_address=data[-2]
        city=data[-1].split(',')[0]
        state=data[-1].split(',')[1].split(' ')[1]
        zip=data[-1].split(',')[1].split(' ')[2]
        street_address=data[-2]
        if "Some providers" in data[1]:
            del data[1]
        phone=data[1].replace('1-855-WH-APPTS','')
        store.append("https://whitehouseclinics.com")
        store.append(location_name[index])
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.strip())
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation)
        store.append("https://whitehouseclinics.com/locations-hours")
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.strip() if type(x) == str else x for x in store]
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
