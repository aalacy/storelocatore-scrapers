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
    base_url = "https://vasafitness.com"
    r = session.get("https://vasafitness.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"marker"}):
        location_request = session.get(location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        if location_soup.find("h4",text=re.compile("Coming Soon")):
            continue
        address = list(location_soup.find("div",{'class':"loc-address"}).stripped_strings)
        hours = " ".join(list(location_soup.find("div",{'id':"loc-accordion"}).stripped_strings))
        if location_soup.find("a",{'href':re.compile("tel:")}) == None:
            phone = "<MISSING>"
        else:
            phone = location_soup.find("a",{'href':re.compile("tel:")})["href"].replace("tel: ","")
        name = address[1].split(",")[-1].split(" ")[-2].upper()
        name1 = location_soup.find("h1",{"class":"text-uppercase"}).text
        store = []
        store.append("https://vasafitness.com")
        store.append(name1)
        store.append(address[0])
        store.append(address[1].split(",")[-2].strip())
        store.append(address[1].split(",")[-1].split(" ")[-2])
        store.append(address[1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.strip())
        store.append("<MISSING>")
        store.append(location["data-latt"])
        store.append(location["data-lngg"])
        store.append(hours)
        # if store[-1].count("Closed") > 6:
        #     continue
        store.append(location.find("a")["href"])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
