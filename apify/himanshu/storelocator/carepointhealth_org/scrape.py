import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',    
    }
    base_url = "https://carepointhealth.org/"
    for i in range(0,9):
        r = session.get("https://carepointhealth.org/wp-json/newfangled-base/v1/locations?page=1&per_page=10",headers=headers).json()[str(i)]
        soup = BeautifulSoup(r,"html5lib")
        data = soup.find("div",{"class":"nf-card-text"})
        page_url = data.find("a")['href']
        latitude = data.find("a")['data-lat']
        longitude = data.find("a")['data-lng']
        location_name = data.find("a").text
        phone = list(data.find("div",{"class":"popup-content"}).stripped_strings)[1].replace("Phone:","").strip()
        addr = list(data.find("div",{"class":"nf-card-excerpt"}).stripped_strings)
        if len(addr) == 1:
            street_address = addr[0].split(",")[0]
            city = addr[0].split(",")[1]
            state = addr[0].split(",")[-1].split(" ")[1]
            zipp = addr[0].split(",")[-1].split(" ")[2]
        elif len(addr) == 2 :
            street_address = addr[0]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[1].replace("NJ\xa007030","NJ 07030").split(" ")[1]
            zipp = addr[1].split(",")[1].replace("NJ\xa007030","NJ 07030").split(" ")[2]
        else:
            street_address = addr[1]
            city = addr[2].split(",")[0]
            state = addr[2].split(",")[1].replace("\xa0"," ").strip().split(" ")[0]
            zipp = addr[2].split(",")[1].replace("\xa0"," ").strip().split(" ")[1]
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")   
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("Carepoint Health")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        yield store
    
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

