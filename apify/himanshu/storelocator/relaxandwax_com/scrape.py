import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('relaxandwax_com')



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
    
    base_url = "http://www.relaxandwax.com"
    dt='lat=33.4052217&lng=-86.87547819999998&radius=100000000'
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    ,
    "Accept":'application/json, text/javascript, */*; q=0.01'
    }
    r = session.post('https://www.relaxandwax.com/GoogleMaps/store_locator.php',data = dt,headers = headers).json()
    return_main_object = []
    for loc in r:
        store=[]
        hour=''
        madd=loc['address'].split(',')
        city="<INACCESSIBLE>"
        page_url = ''
        if len(madd)==1:

            madd=loc['address'].strip().split(' ')
            zip=madd[-1].strip()
            state=madd[-2].strip()
            city = " ".join(madd[-4:-2]).replace('B','').strip()
            del madd[-1]
            del madd[-1]
            address=' '.join(madd).strip()
            
        elif len(madd)==3:
            
            address=madd[0].strip()
            city=madd[-2].strip()
            state=madd[-1].strip().split(' ')[0].strip()
            zip=madd[-1].strip().split(' ')[1].strip()
        else:
            # logger.info(madd)
            state = madd[-1].split()[-2]
            zip = madd[-1].split()[-1]
            if len(madd[-1].split()) > 2:
                address= madd[0].replace('\r\n',' ')
                city = madd[-1].split()[0]
                
                # logger.info(address,city,state,zip)
            else:
                if len( madd[0].split()) ==3:
                    address =  "".join(madd[0]).strip()
                    city = "<MISSING>"
                elif len( madd[0].split()) ==8:
                    address =  " ".join(madd[0].split()[:-2]).strip()
                    city = " ".join(madd[0].split()[-2:]).strip()
                else:
                    address = " ".join(madd[0].split()[:-1]).strip()
                    city = madd[0].split()[-1].strip()
            
        store.append(base_url)
        store.append(loc['name'].replace('&','And').strip())
        store.append(address.strip())
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append(loc['id'])
        if loc['telephone']:
            store.append(loc['telephone'])
        else:
            store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(loc['lat'])
        store.append(loc['lng'])
        store.append("<MISSING>")
        store.append('<MISSING>')
        # logger.info(str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
