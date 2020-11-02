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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://www.subbys.com"
    return_main_object=[]
    link = base_url+'/locations'
    r = session.get(link)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find_all(class_='wsite-multicol-col')
    for i in range(len(main)):
        madd=list(main[i].stripped_strings)
        name=madd[0].encode("ascii", "replace").decode().replace("?","")
        address=madd[1].encode("ascii", "replace").decode().replace("?","")
        ct=madd[2].split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        country="US"
        phone=madd[-1].encode("ascii", "replace").decode().replace("?","").replace('Phone:','').strip()
        store = [base_url,link,name,address,city,state,zip,country,"<MISSING>",phone,"<MISSING>","<MISSING>","<MISSING>","<MISSING>"]
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
