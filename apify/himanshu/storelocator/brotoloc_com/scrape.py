import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('brotoloc_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            
            writer.writerow(row)


def fetch_data():
    addressess123=[]
    locator_domain='https://www.brotoloc.com/'
    vurl = "https://fairview.org/coveo/rest/v2/"
    urls =['https://www.brotoloc.com/eau_claire_group_homes.phtml','https://www.brotoloc.com/western_rivers_group_homes.phtml']
    r2 = session.get("https://www.brotoloc.com/fox_valley_group_homes.phtml")
    soup2 = BeautifulSoup(r2.text, "html5lib")
    for data in soup2.find_all("p",{"class":"nomargin"}):
        full = list(soup2.find("div",{"id":data.find("span",{"class":"strong-orange"})['id'].replace("_info",'')}).stripped_strings)
        street_address = full[0]
        city = full[1].split( )[0]
        state = full[1].split( )[1].strip().split( )[0]
        zipp = full[1].split( )[2]
        phone = full[2]
        page_url = '<MISSING>'
        hours1='<MISSING>'
        location_name = data.text.strip().split("{ ")[0]
        latitude = '<MISSING>'
        longitude = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, hours1, page_url]
        
        # if store[2]  in addressess123:
        #     continue
        # addressess123.append(store[2])
        # logger.info(store)
        yield store
        # logger.info(location_name)
    for value in urls:
        r1 = session.get(value)
        soup1 = BeautifulSoup(r1.text, "html5lib")
        for data in soup1.find_all("p",{"class":"nomargin"}):
            full = soup1.find("div",{"id":data.find("span",{"class":"strong-orange"})['id'].replace("_info",'')})
            street_address = list(full.stripped_strings)[0].split("•")[0]
            city = list(full.stripped_strings)[0].split("•")[1].split(",")[0]
            state = list(full.stripped_strings)[0].split("•")[1].split(",")[1].strip().split(" ")[0]
            zipp = list(full.stripped_strings)[0].split("•")[1].split(",")[1].strip().split(" ")[1]
            phone = list(full.stripped_strings)[0].split("•")[2].strip()
            page_url = '<MISSING>'
            hours1='<MISSING>'
            location_name =data.text.strip().split("{ ")[0]
            latitude = '<MISSING>'
            longitude = '<MISSING>'
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours1, page_url]
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            
            # if store[2]  in addressess123:
            #     continue
            # addressess123.append(store[2])
            # logger.info(store)
            yield store


          
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
