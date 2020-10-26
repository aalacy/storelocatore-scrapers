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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://savoypizza.com"
    r = session.get("https://savoypizza.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("nav",{"class":"locationsNav"}).find_all("a"):
        page_url = location["href"]
        # print(page_url)
        location_request = session.get(page_url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("div",{'class':"main"}).find("h1").text
        address = list(location_soup.find("div",{'class':"main"}).find_all("p")[0].stripped_strings)
        hours = " ".join(list(location_soup.find("div",{'class':"main"}).find_all("p")[1].stripped_strings)).replace("Hours:","").replace(" •",":").strip()
        if "coming" in hours.lower():
            continue
        lat = location_soup.find("div",{'class':"main"}).find("a",{'class':"map"})["data-lat"]
        lng = location_soup.find("div",{'class':"main"}).find("a",{'class':"map"})["data-lng"]
        store = []
        store.append("https://savoypizza.com")
        store.append(page_url)
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1].split(" ")[-2])
        store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[-1].replace("\u202d","").replace("\u202c","") if len(address) != 2 else "<MISSING>")
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
