
import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "https://www.harveysfurniture.co.uk/"
    r =  session.get("https://www.harveysfurniture.co.uk/stores/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml") 
    # print(soup)   
    for link in soup.find_all("a",{"class":"btn-details btn-type1"}):
        page_url = link['href']
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("h1",{"class":"title"}).text.strip()
        # print(location_name)
        addr = list(soup1.find("div", {"class":"info-main info-main--address"}).find("p",{"class":"address"}).stripped_strings)
        street_address = " ".join(addr[:-1])
        city = location_name.replace("(h)","").strip()
        state = "<MISSING>"
        zipp = addr[-1]
        phone =soup1.find("p",{"class":"phone"}).text.strip()
        store_number = page_url.split("h--")[-1]
        coord = soup1.find(lambda tag: (tag.name== "script") and '"lat"' in tag.text).text
        latitude = coord.split('"lat":')[1].split(",")[0].strip()
        longitude = coord.split('"lng":')[1].split(",")[0].strip()
        hours_of_operation = " ".join(list(soup1.find("ul",{"class":"hours-list"}).stripped_strings))
        

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("UK")
        store.append(store_number)
        store.append(phone )
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # print("data===="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
