import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ems_com')



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
    base_url ="https://www.ems.com"
    return_main_object=[]
    output=[]
    addressess =[]
    zps=sgzip.for_radius(100)
    for zp in zps:
        try:
            r = session.get(base_url+"/on/demandware.store/Sites-EMS-Site/default/Stores-GetNearestStores?lat=&long=&countryCode=US&distanceUnit=mi&maxdistance=100&zipCode="+zp).json()
        except:
            continue

        for i in r['stores']:
            address=r['stores'][i]['address1'].strip()
            if r['stores'][i]['address2']:
                address+=' '+r['stores'][i]['address2'].strip()
            page_url = "https://www.ems.com/store-details?StoreID="+str([i][-1])
            # logger.info(page_url)
            r1 = session.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            h1 = soup1.find("div",{"class":"store-info clearfix"}).find("div",{"class":"right"})
            hours_of_operation = re.sub(r"\s+", " ", h1.text)

            # logger.info(hours_of_operation)

            # logger.info(r['stores'][i])
            name=r['stores'][i]['name'].strip()
            city=r['stores'][i]['city'].strip()
            state=r['stores'][i]['stateCode'].strip()
            zip=r['stores'][i]['postalCode'].strip()
            phone=r['stores'][i]['phone'].strip()
            country=r['stores'][i]['countryCode'].strip()
            lat=r['stores'][i]['latitude'].strip()
            lng=r['stores'][i]['longitude'].strip()
            hour=r['stores'][i]['storeHours'].replace('<br />',' ').replace('<br>',' ').replace('<!--',' ').replace('-->',' ').strip()
            hour=re.sub(r'\s+',' ',hour)
            if "Hours" not in hour:
                hour=''
            storeno=i
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
            store.append("<MISSING>")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            store.append(page_url)
            # adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
            # if adrr not in output:
            #     output.append(adrr)
            yield store
      
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
