import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    
    base_url = "https://expstores.com/"
    soup = bs(session.get(base_url).content, "lxml")
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    for url in soup.find_all("a",{"class":re.compile("mpfy-pin mpfy-pin-id-")}):
        
        store_number = url['data-id']
        page_url = url['href']
    
        location_soup = bs(session.get(page_url,headers=headers).content, "lxml")
        addr = list(location_soup.find("div", {"class":"mpfy-p-holder"}).stripped_strings)
        location_name = addr[0]
        
       
        if addr[-1] == 'Philadelphia area':
            del addr[-1]
        if len(addr) == 7 or len(addr) == 6:
            street_address = addr[3]
            zipp = addr[4].split()[-1]
            if re.findall(r'[A-Z]{2}',addr[4]):
                state = addr[4].split()[-2]
                city = " ".join(addr[4].split()[:-2])
            else:
                if len(addr[4].split()) == 2:
                    state = "<MISSING>"
                    city = addr[4].split()[0]
                else:
                    state = " ".join(addr[4].split()[2:4])
                    city = " ".join(addr[4].split()[0:2])
        else:
            street_address = " ".join(addr[3:5])
            state = addr[-3].split()[-2]
            city = " ".join(addr[-3].split()[:-2])
            zipp = addr[-3].split()[-1]
        if addr[-1] == "USA":
            phone = "<MISSING>"
        else:
            phone = addr[-1].replace("/30","")

        coords = location_soup.find("a",{"class":"mpfy-p-bg-gray mpfy-p-color-accent-background"})['href']
        lat = coords.split("=")[-1].split(",")[0]
        lng = coords.split("=")[-1].split(",")[1]

        
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
        
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
