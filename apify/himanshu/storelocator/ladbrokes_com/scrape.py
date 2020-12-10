import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ladbrokes_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressesess=[]
    headers = {
    'content-type': "application/x-www-form-urlencoded",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    }
    base_url = "http://ladbrokes.com"
    r_list = ["https://viewer.blipstar.com/searchdbnew?uid=2470030&lat=54.630057&lng=-3.550830&type=nearest&value=100000&keyword=&max=10000&sp=CA14%203QB&ha=no&htf=1&son=&product=&product2=&product3=&cnt=&acc=&mb=false&state=&ooc=0&r=0.1969129058158794",
            "https://viewer.blipstar.com/searchdbnew?uid=2470030&lat=51.5284541234394&lng=-0.154586637827429&type=nearest&value=100000&keyword=&max=100000&sp=NW1&ha=no&htf=1&son=&product=&product2=&product3=&cnt=&acc=&mb=false&state=&ooc=0&r=0.1874606795247602"]
    for r_loc in r_list:
        
        r = session.get(r_loc,headers=headers).json()
        
        for index,anchor in enumerate(r):
            if index >=1:
                # logger.info(anchor['a'])
                soup = BeautifulSoup(anchor['a'],'lxml')
                state = soup.find("span",{"class":"storecity"}).text.lower()
                zipp = soup.find("span",{"class":"storepostalcode"}).text
                
                adr = BeautifulSoup(anchor['a'],'lxml')
                city = adr.find("span",class_="storecity").text.strip()
                zipp  = adr.find("span",class_="storepostalcode").text.strip()
                state = anchor['c']
                street_address =(adr.text.strip().replace(city,"").replace(zipp,''))
                # logger.info(state)
                # city = anchor['ad'].split(",")[1].strip().lower()
                location_name = anchor['n']
                store_number = location_name.split()[-1].strip()
                # if "BS16 5UJ" in zipp :
                #     street_address = city
                #     city = state

                # logger.info(store_number)
                # if anchor["w"]:
                #     page_url =  anchor["w"]
                # else:
                page_url = "<MISSING>"
                phone = anchor['p']
                hours ='mon '+anchor['mon']+ ' tue ' + anchor['tue']+' wed '+ anchor['wed']+ ' thu ' + anchor['thu']+' fri '+anchor['fri']+' sat '+anchor['sat']+' sun '+anchor['sun']
                location_type = "<MISSING>"
                latitude = anchor['lat']
                longitude = anchor['lng']
                store = []
                store.append('http://ladbrokes.com')
                store.append(location_name)
                store.append(street_address.replace("Shoping Centre","").replace("Shopping Centre",""))
                store.append(city)
                store.append(state)
                store.append(zipp if zipp else "<MISSING>")
                store.append("UK")
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours)
                store.append(page_url)
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                if store[2] in addressesess:
                    continue
                addressesess.append(store[2])
                # logger.info("data == "+str(store))
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
