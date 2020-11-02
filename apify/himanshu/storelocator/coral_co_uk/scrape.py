import csv
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
import json
session = SgRequests()
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('coral_co_uk')


def write_output(data):
	with open('data.csv', mode='w',newline="") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
  

    returnres=[]
    base_url="https://coral.co.uk/"
    # vik
    link="https://viewer.blipstar.com/searchdbnew?uid=4566046&lat=51.5284541234394&lng=-0.154586637827429&type=nearest&value=2000&keyword=&max=10000&sp=&ha=no&htf=1&son=&product=&product2=&product3=&cnt=&acc=&mb=false&state=&ooc=0&r=0.8477408509027549"
    r=session.get(link,headers=headers).json()
    
    for item  in r[1:]:
        soup = BeautifulSoup(item['a'],'lxml')
        addr = item['ad'].split(",")
        if len(addr)==4:
            street_address=" ".join(addr[:3]).strip()
            state = addr[-2].strip()
        
        elif len(addr) ==3:
            street_address  = addr[0]
            state = addr[-2].strip()
        elif len(addr) == 2:
            street_address = addr[0]
            state = "<MISSING>"
        try:
            city=soup.find("span",{"class":"storecity"}).text
        except:
            city = "<MISSING>"  
        if "Unit" not in street_address:
            street_address = street_address.split("  ")[0].strip()
        else:
            street_address = " ".join(street_address.split("  ")[:-1]).strip()
        
        page_url = item['w'].strip()
        location_name=item['n'].strip()
        zipp=item['pc']
        phone=str(item['p']).strip()
        latitude=item['lat']
        longitude=item['lng']
        hour = ' mon '+ item['mon']+ ' thu ' +item['thu']+ ' wed '+item['wed']+' tue '+item['tue']+' fri '+ item['fri']+' sat '+ item['sat']+' sun '+item['sun']
        hour=re.sub(r'\s+'," ",item['mon'].strip()).strip()
        store =[]
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")
        store.append("UK")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append("<MISSING>")
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # logger.info(store)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
