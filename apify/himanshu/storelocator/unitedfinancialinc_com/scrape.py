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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://unitedfinancialinc.com/"
    return_main_object=[]
    headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36","Content-Type": "application/json;charset=UTF-8"}
    dt='{"bounds":[{"Latitude":-67.8382886748674,"Longitude":-180},{"Latitude":85.57569667044429,"Longitude":180},{"Latitude":42.106342,"Longitude":-72.622995}]}'
    r = session.post("https://www.bankatunited.com/DataAccess/LocationService.svc/GetLocations",headers=headers,data=dt).json()
    for loc in r['d']:
        cleanr = re.compile('<.*?>')
        madd=loc['Address'].split('<br />')
        if len(madd)>2:
            if "Tel" not in madd[2]:
                del madd[0]
        address=madd[0].replace('&nbsp;',' ').strip()
        address=re.sub(cleanr, '',address)
        ct=madd[1].split(',')
        if len(ct)>1:
            city=ct[0].replace('\r\n','').replace('\&nbsp;',' ').strip()
            state=ct[1].strip().split(' ')[0].replace('\&nbsp;',' ').strip()
            zip=ct[1].strip().split(' ')[1].replace('\&nbsp;',' ').strip()
        else:
             ct=madd[1].strip().split(' ')
             city=ct[0].replace('\r\n','').replace('\&nbsp;',' ').strip()
             state=ct[1].replace('\&nbsp;',' ').strip()
             zip=ct[2].replace('\&nbsp;',' ').strip()
        phone=''
        if len(madd)>2:
            phone=madd[2].replace('\r\nTel:','').strip()
        name=loc['Name'].strip()
        hour=loc['Content'].strip()
        hour = re.sub(cleanr, '', hour)
        hour = re.sub(r'\s+', ' ', hour).replace(' &ndash;','')
        lat=loc['Coordinates']['Latitude']
        lng=loc['Coordinates']['Longitude']
        country="US"
        storeno=''
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
        store.append("unitedfinancialinc")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
