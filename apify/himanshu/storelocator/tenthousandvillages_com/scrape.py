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
    base_url = "https://www.tenthousandvillages.com/"
    return_main_object=[]
    r = session.get(base_url+'/store-locator/')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('select',{"name":"st_state"}).find_all('option')
    del main[0]
    for opt in main:
        r1 = session.get(base_url+'/store-locator/ajaxdata/result/?country=US&state='+opt['value'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=json.loads(r1.text.split('<jsonmapdata><![CDATA[')[1].split(']]></jsonmapdata>')[0].strip())
        sno=soup1.find_all('storelocator_id')
        i=0
        for loc in main1['macDoList']:
            storeno=sno[i].text.strip()
            i=i+1
            name=loc['data']['name']
            cleanr = re.compile('<.*?>')
            name = re.sub(cleanr, '', name)
            phone=loc['data']['phone']
            address=loc['data']['address'].replace('<br>',' ').replace('<br />',' ')
            address=re.sub(r'\s+',' ',address)
            city=loc['data']['city']
            state=loc['data']['state']
            zip=loc['data']['zip']
            lat=loc['lat'] if loc['lat']!="0" else ''
            lng=loc['lng'] if loc['lng']!="0" else ''
            country="US"
            hour=''
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
            store.append("tenthousandvillages")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
