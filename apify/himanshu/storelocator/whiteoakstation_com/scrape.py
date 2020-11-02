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
    base_url = "https://www.whiteoakstation.com"
    r = session.get(base_url+"/find-us-map/")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('script')
    for dt in main:
        if "var map1" in dt.text:
            for loc in json.loads(dt.text.split('"places":')[1].split(',"styles"')[0],strict=False):
                name=loc['title'].strip()
                lat=loc['location']['lat'].strip()
                lng=loc['location']['lng'].strip()
                state=loc['location']['state'].strip()
                country=loc['location']['country'].strip()
                phone=loc['location']['extra_fields']['phone'].strip()
                storeno=loc['id']
                zip="<MISSING>"
                if country=="United States":
                    country="US"
                madd=loc['address'].split(',')
                if "USA" in madd[-1]:
                    del madd[-1]
                if len(madd)==3:
                    address=madd[0]
                    city=madd[1]
                    st=madd[2].strip().split(' ')
                    if len(st)==1:
                        state=madd[2].strip()
                    else:
                        state=st[0].strip()
                        zip=st[1].strip()
                elif len(madd)==2:
                    address=madd[0]
                    city="<INACCESSIBLE>"
                    st=madd[1].strip().split(' ')
                    if len(st)==1:
                        state=madd[1].strip()
                    else:
                        state=st[0].strip()
                        zip=st[1].strip()
                else:
                    madd=loc['address'].split(' ')
                    zip=madd[-1].strip()
                    del madd[-1]
                    state=madd[-1].strip()
                    del madd[-1]
                    city=madd[-1].strip()
                    del madd[-1]
                    address=' '.join(madd).strip()
                store=[]
                store.append(base_url)
                store.append(name)
                store.append(address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append("US")
                store.append(storeno)
                store.append(phone)
                store.append("whiteoakstation")
                store.append(lat)
                store.append(lng)
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
