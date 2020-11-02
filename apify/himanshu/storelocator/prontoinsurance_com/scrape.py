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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.prontoinsurance.com"
    r = session.get("https://products.prontoinsurance.com/agency-locator",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    addresses = []
    for location in soup.find_all("div",{'class':"location-tab"}):
        page_url = "https://products.prontoinsurance.com" + location.find("a",{"class":'details-link'})["href"]
        location_request = session.get(page_url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        hours = ""
        for hour in location_soup.find_all("h5",text=re.compile("Hours")):
            hours = hours + " " + " ".join(list(hour.parent.stripped_strings))
        name = location.find('h5').text
        address_1 = location.find('span',{'class':"address1"}).text
        address_2 = location.find('span',{'class':"address2"}).text
        if address_1 in addresses:
            continue
        addresses.append(address_1)
        for state in address_2.split(" "):
            if len(state) == 2:
                store_state = state
        if address_1 == "":
            continue
        phone = location.find('a',{'href':"#"})["data-phone"].strip().replace("Ph:","").replace("PH:","")
        store = []
        store.append("https://www.prontoinsurance.com")
        store.append(name)
        store.append(address_1)
        store.append(address_2.split(",")[0])
        store.append(store_state)
        store.append(address_2.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone != "" else "<MISSING>")
        store.append("<MISSING>")
        if "-"  not in location["data-lat"]:
            store.append(location["data-lat"])
            store.append(location["data-lng"])
        else:
            store.append(location["data-lng"])
            store.append(location["data-lat"])
        store.append(hours if hours else "<MISSING>")
        store.append(page_url)
        for i in range(len(store)):
            if store[i] == "":
                store[i] = "<MISSING>"
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
