import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('capmat_com')



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
    base_url = "https://capmat.com"
    r = session.get(base_url+"/Contact.do")
    soup=BeautifulSoup(r.text ,"lxml")
    # logger.info(r.text.split('v-google-map='))
    lat_and_log ={}
    for j in json.loads(soup.find("div",class_="flex xl6 md6 sm12 xs12").find("v-select")[':items']):
        lat_and_log[j['name']]={"latitude":j['latitude'],"longitude":j['longitude'],"aboutUrl":j['aboutUrl']}
    # logger.info(lat_and_log)
    # exit()
    return_main_object = []
    cnt=0
    main=soup.find('div',{"id":"gw-contact"}).find('div',{"class":"layout row wrap"}).find_all('div',{"class":"layout row wrap"})
    for atag in main:
        loc=list(atag.stripped_strings)
        name=loc[0]
        address=loc[1]
        cnt=cnt+1
        ct=loc[2].split(',')
        if len(ct) == 1:
            address=loc[1]+' '+loc[2]
            ct=loc[3].split(',')
            phone=loc[4].replace('PH:','').strip()
        else:
            phone=loc[3].replace('PH:','').strip()
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zipp=ct[1].strip().split(' ')[-1].strip()
        
        
        hour= re.sub(r"\s+", " ", loc[-1])

        if "Hours" in loc[-2]:
            hour+= " " + re.sub(r"\s+", " ", loc[-2])
        lat = lat_and_log[name]['latitude']
        lng = lat_and_log[name]['longitude']
        
        # lt=r.text.split('markers'+str(cnt)+' = {')[1].split('{')[1].split('}')[0].split(',')
        # lat=lt[0].replace("latitude:",'').strip()
        # lng=lt[1].replace("longitude:",'').strip()
        store = []
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hour.replace('Hours: ',''))
        store.append("https://capmat.com/"+lat_and_log[name]['aboutUrl'] if lat_and_log[name]['aboutUrl'] != None else "<NISSING>" )
        store = [str(x).replace("–","-").encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
