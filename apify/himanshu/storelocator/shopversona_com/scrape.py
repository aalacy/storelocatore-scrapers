import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
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
    base_url = "https://www.shopversona.com"

    r = session.get("https://www.shopversona.com/versonastores.cfm")
    soup = BeautifulSoup(r.text, "lxml")
    states = soup.find("select",{"name":"locSt"}).find_all("option")[1:]
    for state in states:
        r1 = session.get("https://www.shopversona.com/versonastores.cfm?&locSt="+str(state['value']))
        
        soup1 = BeautifulSoup(r1.text, "lxml")
        data = soup1.find_all("div",{"class":"mapAddress"})
        for info in data:
            
            latitude = info.find("h4")['onclick'].split(",")[1]
            longitude = info.find("h4")['onclick'].split(",")[2].replace(");","")
            addr = list(info.stripped_strings)
            if "Coming Soon" in  addr[1]:
                continue
            if "Now Open" in addr[1]:
                del addr[1]
            location_name = addr[1]
            street_address = addr[2].split("(")[0].strip()
            city = addr[0].split(",")[0]
            state = addr[0].split(",")[1].strip()
            phone = addr[3]
            if len(addr) == 7:
                hours_of_operation = " ".join(addr[4:6]).replace("|","-")
            else:
                hours_of_operation = "<MISSING>"
            page_url = "https://www.shopversona.com/versonastores.cfm?&locSt="+str(state)


            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append("<MISSING>")
            store.append("US")
            store.append("<MISSING>") 
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)         
            yield store 

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
