import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import phonenumbers
from datetime import datetime
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    base_url = "https://www.afcurgentcare.com/"

    json_data = session.post("https://www.afcurgentcare.com/locations/?CallAjax=GetLocations").json()
    
    for data in json_data:
        location_name = data['FranchiseLocationName']
        street_address = data['Address1']
        
        if data['Address2']:
            street_address += " " +  data['Address2']
        city = data['City']
        state = data['State']
        zipp = data['ZipCode']
        country_code = data['Country']
        store_number = data['FranchiseLocationID']
        phone = phonenumbers.format_number(phonenumbers.parse(data['Phone'], 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
        lat = data['Latitude']
        lng = data['Longitude']
        page_url = "https://www.afcurgentcare.com"+data['Path']
        if data['LocationHours']:
            interval = json.loads('{ "data":[' + data['LocationHours'].replace("][","},{").replace("[","{").replace("]","}") + ']}')['data']
            hours = ''
            for hr in interval:
                hours += " "+ hr['Interval'] +" "+ hr['OpenTime'] +" - "+ hr['CloseTime'] +" "
        else:
            try:
                location_soup = bs(session.get(page_url).content, "lxml")
                hours = " ".join(list(location_soup.find("ul",{"class":"hours ui-repeater"}).stripped_strings))
            except:
                hours = "<MISSING>"

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours.replace('Please call for office hours See More Hours','OPEN 7 DAYS A WEEK'))
        store.append(page_url.strip())     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
       
        yield store
       
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
