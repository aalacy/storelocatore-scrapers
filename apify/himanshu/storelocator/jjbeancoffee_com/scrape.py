import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    
    }
    locator_domain = "https://jjbeancoffee.com"
    page_url = "https://jjbeancoffee.com/locations/"
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text,"lxml")


    for i in soup.find_all("header",{"class":"entry-header"})[1:]:
        # print(i.prettify())
        # print("========================")
        location_name = i.find("h2",{"class":"entry-title"}).text
        data1 = i.find("p").find("em")
        raw_add = data1.find("a").text.split(",")
       # print(raw_add)
        street_address = raw_add[0]
        city = raw_add[-1]
        state = "BC"
        zipp = "<MISSING>"
        country_code = "CA"
        store_number = i.find("a")["name"].replace("location-","")
        raw_data = data1.text.split(":")
        #print(raw_data)
        phone = raw_data[2].replace("Hours","").replace(" ext. 4Hours","").replace(" ext. 4","").strip()
        location_type = "<MISSING>"

        if len(data1.find("a")["href"].split("/"))>= 6:
            raw_href = data1.find("a")["href"].split("/")[6].split(",")
            lat = raw_href[0].replace("@","")
            lng = raw_href[1]
        else:
            lat = "<MISSING>"
            lng = "<MISSING>"

        hours_of_operation = " ".join(raw_data[3:]).strip()
    
    
        store = []
        store.append(locator_domain)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hours_of_operation)
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
