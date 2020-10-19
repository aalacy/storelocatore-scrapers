import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    base_url = "https://parksterlingbank.com"
    for i in range(1,11):
        r = session.get("https://www.southstatebank.com/api/locationsearch/Index?lat=34.037714&lng=-81.0776477&searchQuery=&safeDepositBox=&openSaturday=&driveThru=&atmDeposits=&atm24=&atmLobby=&atm24Deposits=&pageNum="+str(i)+"&searchTerm=",headers=headers).json()['Entities']
        for val in r:
            street_address = val['Address']['Line1']
            city = val['Address']['City']
            state = val['Address']['Region']
            zipp = val['Address']['PostalCode']
            store_number = val['Meta']['Id']
            phone = val['MainPhoneForDisplay']
            latitude = val['YextDisplayCoordinate']['Latitude']
            longitude = val['YextDisplayCoordinate']['Longitude']
            hours_of_operation = "Lobby Hours: "+",".join(val['LobbyHours']) +", "+"Drive Thru Hours: "+ ",".join(val['DriveThruHours'])
            store=[]
            store.append(base_url)
            store.append("<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append(store_number)
            store.append(phone if phone else "<MISSING>")
            store.append("south state bank")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
            store.append("<MISSING>")
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

