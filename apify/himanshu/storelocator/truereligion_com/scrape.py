import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('truereligion_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.truereligion.com"
    data = '{"request":{"appkey":"1C4F6E2A-C3CC-11E2-A252-16BE05D25870","formdata":{"geoip":false,"dataview":"store_default","limit":500,"geolocs":{"geoloc":[{"addressline":"","country":"US","latitude":"","longitude":"","state":"","province":"","city":"","address1":"","postalcode":""}]},"searchradius":"5000","stateonly":"","where":{"or":{"fullprice":{"eq":""},"outlet":{"eq":""},"factory":{"eq":""},"internationalwholesale":{"eq":""}}},"false":"0"}}}'
    json_data = session.post('https://hosted.where2getit.com/truereligion/rest/locatorsearch?like=0.09181422211445356', data=data).json()['response']['collection']
    # logger.info(json_data)
    addressess = []
    
    for poi in json_data:
        location_type = poi['icon']
        if location_type == "True_International":
            continue
        name = poi['name']
        address = (poi['address1'] +" "+ str(poi['address2'])).replace("None","").strip()
        storeno = poi['clientkey']
        city = poi['city']
        country = poi['country']
        if country not in ['CA',"US"]:
            continue
        state = poi['state']
        lat = poi['latitude']
        lng = poi['longitude']
        phone = poi['phone']
        zipp = poi['postalcode']
        hour=''
        if poi['monopen']:
            hour+=" Monday : "+poi['monopen']+" "+poi['monclose']
        if poi['tueopen']:
            hour+=" Tuesday : "+poi['tueopen']+" "+poi['tueclose']
        if poi['wedopen']:
            hour+=" Wednesday : "+poi['wedopen']+" "+poi['wedclose']
        if poi['thropen']:
            hour+=" Thursday : "+poi['thropen']+" "+poi['thrclose']
        if poi['friopen']:
            hour+=" Friday : "+poi['friopen']+" "+poi['friclose']
        if poi['satopen']:
            hour+=" Saturday : "+poi['satopen']+" "+poi['satclose']
        if poi['sunopen']:
            hour+=" Sunday : "+poi['sunopen']+" "+poi['sunclose']
        page_url = "http://locations.truereligion.com/ny/elmhurst/"+str(storeno)+"/?utm_source=true%20religion&utm_medium=Store%20Locator&utm_campaign=true%20religion%20Store%20Locator"

        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type)
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append(page_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store 

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
