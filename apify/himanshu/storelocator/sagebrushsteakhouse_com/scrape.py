import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import urllib3
import requests

session = SgRequests()

requests.packages.urllib3.disable_warnings()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }

    base_url= "https://www.sagebrushsteakhouse.com/"
    r = session.get(base_url,headers=headers,verify=False)
    soup= BeautifulSoup(r.text,"lxml")

    for link in soup.find("ul",{"class":"subnavigation"}).find_all("a"):
        location_soup = BeautifulSoup(session.get(link.get('href')).content,"lxml")

        for data in location_soup.find_all("div",{"class":"t-edit-helper"})[1:]:

            address = list(data.stripped_strings)
            
            location_name = address[0]
            if location_name == "SAGEBRUSH OF":
                location_name += " "+ address[1]
                del address[1]
            if "Temporarily Closed" in address[1]:
                del address[1]
            street_address = address[3]
            if address[4].count(",") == 2:
                city = address[4].split(",")[0].strip()
                state = address[4].split(",")[1].strip()
                zipp = address[4].split(",")[2].strip()
            else:
                city = address[4].split(",")[0]
                state = address[4].split(",")[1].split()[0]
                zipp = address[4].split(",")[1].split()[1]
            phone = address[2]

            hours = " ".join(address[6:10])

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours)
            store.append(link.get('href')) 
    
            yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
