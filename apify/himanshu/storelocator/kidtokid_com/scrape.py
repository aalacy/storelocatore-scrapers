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
    base_url = "http://kidtokid.com"
    r = session.get(base_url+"/stores/")
    soup=BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    main=soup.find_all('script')
    for script in main:
        if "var maplistScriptParamsKo" in script.text:
            data=json.loads(script.text.split('var maplistScriptParamsKo = ')[1].split('};')[0]+"}",strict=False)
            for val in data['KOObject'][0]['locations']:
                lat=val['latitude']
                lng=val['longitude']
                r1 = session.get(base_url+'/'+val['title'].lower())
                soup1=BeautifulSoup(r1.text ,"lxml")
                for script1 in soup1.find_all('script'):
                    if "var ajax " in script1.text:
                        link1="http://kidtokid.com/wp-admin/admin-ajax.php"
                        headers = {
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                            'Accept': 'application/json'
                        }
                        dt=script1.text.split('id:')[1].split('}')[0]
                        r3 = session.post(link1,data="action=csl_ajax_loaddtemplate&id="+dt, headers=headers).json()
                        address=r3['response'][0]['address']
                        name=r3['response'][0]['title']
                        city=r3['response'][0]['city']
                        state=r3['response'][0]['state']
                        zip=r3['response'][0]['zip']
                        storeno=r3['response'][0]['id']
                        phone=r3['response'][0]['phone']
                        hour="STORE HOURS:"
                        if r3['response'][0]['hours_F']:
                            hour+=r3['response'][0]['hours_F']+" "
                        if r3['response'][0]['hours_M']:
                            hour+=r3['response'][0]['hours_M']+" "
                        if r3['response'][0]['hours_S']:
                            hour+=r3['response'][0]['hours_S']+" "
                        if r3['response'][0]['hours_SUN']:
                            hour+=r3['response'][0]['hours_SUN']+" "
                        if r3['response'][0]['hours_T']:
                            hour+=r3['response'][0]['hours_T']+" "
                        if r3['response'][0]['hours_TH']:
                            hour+=r3['response'][0]['hours_TH']+" "
                        if r3['response'][0]['hours_W']:
                            hour+=r3['response'][0]['hours_W']+" "
                        hour+=" ,BUY HOURS:"
                        if r3['response'][0]['buy_hours_F']:
                            hour+=r3['response'][0]['buy_hours_F']+" "
                        if r3['response'][0]['buy_hours_M']:
                            hour+=r3['response'][0]['buy_hours_M']+" "
                        if r3['response'][0]['buy_hours_S']:
                            hour+=r3['response'][0]['buy_hours_S']+" "
                        if r3['response'][0]['buy_hours_SUN']:
                            hour+=r3['response'][0]['buy_hours_SUN']+" "
                        if r3['response'][0]['buy_hours_T']:
                            hour+=r3['response'][0]['buy_hours_T']+" "
                        if r3['response'][0]['buy_hours_TH']:
                            hour+=r3['response'][0]['buy_hours_TH']+" "
                        if r3['response'][0]['buy_hours_W']:
                            hour+=r3['response'][0]['buy_hours_W']+" "
                        store=[]
                        store.append(base_url)
                        store.append(name)
                        store.append(address)
                        store.append(city)
                        store.append(state)
                        store.append(zip.split(',')[0])
                        store.append("US")
                        store.append(storeno)
                        store.append(phone)
                        store.append("kidtokid")
                        store.append(lat)
                        store.append(lng)
                        store.append(hour)
                        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
