import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    base_url = "https://www.genesishealth.com"
    r = session.get("https://www.genesishealth.com/facilities/location-search-results/?searchId=cebd1797-017f-ea11-a82a-000d3a611816&sort=13&page=1", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for page in soup.find("div",{"class":"Pagination"}).find_all("option"):
        r1 = session.get(page['value'].replace("~",base_url))
        soup1 = BeautifulSoup(r1.text, "lxml")
        for script in soup1.find("div",{"class":"LocationsList"}).find_all("li"):
            location_name = script.find("a")['title']
            addr = list(script.find("p",{"class":"TheAddress"}).stripped_strings)
            street_address = " ".join(addr[:-1]).split("Suite")[0]
            city = addr[-1].split(",")[0]
            state = addr[-1].split(",")[1].split(" ")[1]
            if len(addr[-1].split(",")[1].split(" ")) == 3:
                zipp = addr[-1].split(",")[1].split(" ")[-1]
            else:
                zipp = "<MISSING>"
            try:
                phone = script.find("span",{"class":"Phone"}).text
            except:
                phone = "<MISSING>"
            
            page_url = base_url + script.find("a",{"class":"Name"})['href'].replace("..","")
            if "&id" in page_url:
                store_number = page_url.split("&id=")[-1]
            else:
                store_number = "<MISSING>"
            
        
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address.replace("Floor",""))
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            # if store[2] in addresses:
            #     continue
            addresses.append(store[2])
            # store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data == "+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
def scrape():

    data = fetch_data()
    write_output(data)

scrape()
