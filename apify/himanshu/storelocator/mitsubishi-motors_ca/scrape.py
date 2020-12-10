import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from googletrans import Translator
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mitsubishi-motors_ca')


translator = Translator()
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.mitsubishi-motors.ca/"
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
        
    link = "https://www.mitsubishi-motors.ca/api/ev_dealer.json"
    json_data = session.get(link, headers=headers).json()
    
    for loc in json_data:
        address = loc['CompanyAddress'].strip()
        name = loc['CompanyName'].strip()
        city = loc['CompanyCity'].strip().capitalize()
        state = loc['ProvinceAbbreviation'].strip()
        zipp = loc['CompanyPostalCode']
        phone = loc['CompanyPhone'].strip()
        lat = loc['Latitude']
        lng = loc['Longitude']
        page_url = loc['PrimaryDomain'] 
        storeno = loc['CompanyId']
        hours='<MISSING>'
        try:
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
        except:
            pass
        try:
            hours= " ".join(list(soup1.find("ul",{"class":"list-unstyled line-height-condensed"}).stripped_strings))
        except:
            pass

        try:
            hours=" ".join(list(soup1.find("ul",{"class":"opening-hours-ul"}).stripped_strings))
        except:
            pass
        try:
            hours=" ".join(list(soup1.find("div",{"id":"Sales36412421385f59c2556d399"}).stripped_strings))
        except:
            pass
    
        try:
            hours=" ".join(list(soup1.find("table",{"class":"grid-y department-hours"}).stripped_strings))
        except:
            pass

        try:
            hours=" ".join(list(soup1.find("table",{"class":"map_open_hours"}).stripped_strings))
        except:
            pass

        try:
            hours=" ".join(list(soup1.find("div",{"class":"map_open_hours"}).stripped_strings))
        except:
            pass

        try:
            hours=" ".join(list(soup1.find("table",{"class":"footer-hours-tabs__box-wrapper"}).stripped_strings))
        except:
            pass

        try:
            hours=" ".join(list(soup1.find("div",{"id":"footer-hours-loc-0-sales"}).stripped_strings))
        except:
            pass
        try:
            hours=" ".join(list(soup1.find("div",{"class":"dynamic-hours parts"}).stripped_strings))
        except:
            pass
        try:
            hours=" ".join(list(soup1.find("ul",{"class":"list-unstyled line-height-condensed"}).stripped_strings))
        except:
            pass
        try:
            hours=" ".join(list(soup1.find("div",{"class":"hours-default"}).stripped_strings))
        except:
            pass
        try:
            hours=" ".join(list(soup1.find("table",{"class":"beaucage_hours"}).stripped_strings))
        except:
            pass
        hours = translator.translate(hours,dest='en').text.split("Service")[0].replace("Opening hours",'').strip()
      
        store=[]
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("CA")
        store.append(storeno)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours.strip())
        store.append(page_url)
        #logger.info("data == "+str(store))
        #logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
          
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
