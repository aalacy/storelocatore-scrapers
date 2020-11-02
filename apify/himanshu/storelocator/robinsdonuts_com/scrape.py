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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.robinsdonuts.com"
    return_main_object = []
    count = 1
    while True:
        r = session.get("http://www.robinsdonuts.com/locations.aspx?address=&city=&Countryui=CA&pageNumber=" + str(count),headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        if soup.find("div",{'class':"location-box margin_t_40 margin-t-20"}) == None:
            break
        for location in soup.find_all("div",{'class':"location-box margin_t_40 margin-t-20"}):
            address = location.find("p",{'class':"fontXXL"}).text
            address2 = location.find("p",{'class':"fontpro under-line"}).text.strip()
            phone = location.find("ul",{'class':"md-li"}).find("p").text.strip()
            geo_location = location.find("a",{'class':"red-line"})["href"]
            store = []
            store.append("http://www.robinsdonuts.com")
            store.append(address)
            store.append(address)
            store.append(address2.split(",")[0])
            store.append(address2.split(",")[1])
            store.append(address2.split(",")[2])
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone if phone != "N/A" else "<MISSING>")
            store.append("robin's")
            store.append(geo_location.split("EndAddress=")[1].split(",")[0] if geo_location.split("EndAddress=")[1].split(",")[0] != "0.0000000000" else "<MISSING>")
            store.append(geo_location.split("EndAddress=")[1].split(",")[1] if geo_location.split("EndAddress=")[1].split(",")[1] != "0.0000000000" else "<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
        count = count + 1
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
