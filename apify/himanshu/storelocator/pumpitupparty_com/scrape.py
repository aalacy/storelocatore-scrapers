import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

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
    base_url = "https://www.pumpitupparty.com"
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36","content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
    zps=sgzip.for_radius(100)
    return_main_object = []
    output=[]
    for zp in zps:
        data="action=bu-search&current-page=https%3A%2F%2Fwww.pumpitupparty.com%2F&redirect=&bu-zipcode="+str(zp)
        try:
            r = session.post(base_url+"/wp-admin/admin-ajax.php",headers=headers,data=data)
            soup=BeautifulSoup(r.text,'lxml')
            if soup.find('script',{"type":"text/javascript"})!=None:
                main=json.loads(soup.find('script',{"type":"text/javascript"}).text.split('var locations = ')[1].split('];')[0]+']'.strip())
                for loc in main:
                    storeno=loc['store_num'].strip()
                    name=loc['store_name'].strip()
                    address=loc['address1'].strip()
                    if loc['address2']:
                        address+=' '+loc['address2']
                    country="US"
                    city=loc['city'].strip()
                    state=loc['state'].strip()
                    zip=loc['zip'].strip()
                    phone=loc['phone'].strip()
                    lat=loc['latitude']
                    lng=loc['longitude']
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
                    store.append("pumpitupparty")
                    store.append(lat if lat else "<MISSING>")
                    store.append(lng if lng else "<MISSING>")
                    store.append(hour if hour else "<MISSING>")
                    adrr=address+' '+city+' '+state+' '+zip
                    if adrr not in output:
                        output.append(adrr)
                        return_main_object.append(store)
        except:
            continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
