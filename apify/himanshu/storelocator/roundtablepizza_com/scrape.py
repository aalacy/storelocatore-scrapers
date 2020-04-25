# coding=UTF-8
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.roundtablepizza.com/"
    data = {"action":"get_locations",
            "geo": "true",
            "zip":"9"}
    r = session.post("https://www.roundtablepizza.com/wp-admin/admin-ajax.php", data=data, headers=headers).json()
    soup = BeautifulSoup(r['markup'], "lxml")
    for data in soup.find_all("div")[7].find_all("div",{"class":"location-list__item js-location clear-inner-divs"}):
        latitude = data['data-lat']
        longitude = data['data-lng']
        addr = list(data.find("address",{"class":"js-location-address"}).stripped_strings)
        street_address = addr[0]
        if "\t\t\t\t\t\t\t\t\t\t" in addr[-1]:
            street_address+=" "+ addr[-1].split("\t\t\t\t\t\t\t\t\t\t")[0]
            city =  addr[-1].split("\t\t\t\t\t\t\t\t\t\t")[1].split(",")[0]
            state = addr[-1].split("\t\t\t\t\t\t\t\t\t\t")[1].split(",")[1].split(" ")[1]
            zipp = addr[-1].split("\t\t\t\t\t\t\t\t\t\t")[1].split(",")[1].split(" ")[2]
        else:
            city = addr[-1].split(",")[0]
            state = addr[-1].split(",")[1].split(" ")[1]
            zipp = addr[-1].split(",")[1].split(" ")[2]
        if "CLOSED" in street_address:
            continue
        try:
            phone = data.find("div",{"class":"location-list__phone"}).text.replace("\t","").replace("\n","").replace("// Store Hours: Thursday, Friday & Saturday, 11:00am - 2:00pm, 5:00pm - 8:00pm","").strip()
        except:
            phone = "<MISSING>"
        try:
            hours = " ".join(list(data.find("div",{"class":re.compile("js-location-hours")}).stripped_strings))
        except:
            hours = "<MISSING>"
        try:
            page_url = data.find("div",{"class":"location-list__action--wrap"}).find("a")['href']
        except:
            page_url = "<MISSING>"

        store = []
        store.append(base_url)
        store.append("<MISSING>")
        store.append(street_address.replace("Online Ordering Coming Soon!",""))
        store.append(city)
        store.append(state)
        store.append(zipp.replace("953636","95363"))
        store.append("US")
        store.append("<MISSING>") 
        store.append(phone)
        store.append("Restaurant")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        yield store

    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
