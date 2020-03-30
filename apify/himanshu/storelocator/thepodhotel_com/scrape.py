import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    base_url = "https://www.thepodhotel.com"
    r = session.get("https://www.thepodhotel.com/locations.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("a",text=re.compile("LEARN MORE")):
        location_request = session.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        details_url = location_soup.find("a",text=re.compile("Location", flags=re.IGNORECASE))["href"]
        details_request = session.get(base_url + details_url,headers=headers)
        details_soup = BeautifulSoup(details_request.text,"lxml")
        location_details = list(details_soup.find("h2",{'class':"wsite-content-title"}).parent.stripped_strings)[:-3]
        if len(location_details[2].split(",")) > 1:
            if len(location_details[3].split(" ")[-1]) != 5:
                del location_details[2]
        if len(location_details[3].split(",")) != 2:
            if len(location_details[3].split(" ")) != 3:
                location_details[2] = " ".join(location_details[2:4])
                del location_details[3]
        for i in range(len(location_details)):
            if "Phone" in location_details[i]:
                phone = location_details[i+1]
        store = []
        store.append("https://www.thepodhotel.com")
        store.append(" ".join(location_details[:2]))
        store.append(location_details[2])
        if len(location_details[3].split(",")) == 2:
            store.append(location_details[3].split(",")[0])
            store.append(location_details[3].split(",")[-1].split(" ")[-2])
            store.append(location_details[3].split(",")[-1].split(" ")[-1].replace("\u200b",""))
        else:
            store.append(location_details[3].split(" ")[0])
            store.append(location_details[3].split(" ")[1])
            store.append(location_details[3].split(" ")[2])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        geo_location = details_soup.find("iframe")["src"]
        store.append(geo_location.split("&lat=")[1].split("&")[0])
        store.append(geo_location.split("&long=")[1].split("&")[0])
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
