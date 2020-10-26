import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rutters_com')




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
    base_url = "https://www.rutters.com/"
    r = session.get(base_url+"/stores/?zip=#locations")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('script')
    for script in main:
        if "var storesJSON" in script.text:
            loc =json.loads(script.text.split('var storesJSON = ')[1].split(']}}};')[0]+"]}}}",strict=False)
            for i in loc:
                store=[]
                country=loc[i]['store_meta']['country']
                hour=""
                if loc[i]['store_meta']['monday']:
                    hour+="Monday : "+loc[i]['store_meta']['monday']+" "
                if loc[i]['store_meta']['tuesday']:
                    hour+="Tuesday : "+loc[i]['store_meta']['tuesday']+" "
                if loc[i]['store_meta']['wednesday']:
                    hour+="Wednesday : "+loc[i]['store_meta']['wednesday']+" "
                if loc[i]['store_meta']['thursday']:
                    hour+="Thursday : "+loc[i]['store_meta']['thursday']+" "
                if loc[i]['store_meta']['friday']:
                    hour+="Friday : "+loc[i]['store_meta']['friday']+" "
                if loc[i]['store_meta']['saturday']:
                    hour+="Saturday : "+loc[i]['store_meta']['saturday']+" "
                if loc[i]['store_meta']['sunday']:
                    hour+="Sunday : "+loc[i]['store_meta']['sunday']+" "
                if country=="USA":
                    country="US"
                store.append(base_url)
                store.append(loc[i]['post_name'])
                store.append(loc[i]['store_meta']['address'])
                store.append(loc[i]['store_meta']['city'])
                store.append(loc[i]['store_meta']['state'])
                store.append(loc[i]['store_meta']['zip'])
                store.append(country)
                store.append(loc[i]['store_meta']['store_number'])
                store.append(loc[i]['store_meta']['phone_number'])
                store.append("rutters")
                store.append(loc[i]['store_meta']['latitude'])
                store.append(loc[i]['store_meta']['longitude'])
                store.append(hour)
                logger.info(store)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()