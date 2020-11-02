import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    base_url = "https://www.jabzboxing.com"
    r = session.get("https://www.jabzboxing.com/find-a-jabz/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"locations-page-one column white-text rel"}):
        location_details = list(location.stripped_strings)
        if len(location_details) < 4:
            continue
        if "COMING SOON" in location_details[0]:
            continue
        if "Suite" in location_details[3]:
            location_details[2] = " ".join(location_details[2:4])
            del location_details[3]
        if "Phone:" in location_details[3]:
            location_details.insert(1,location_details[0])
        if len(location_details[3].split(",")) != 2:
            if len(location_details[3].split(" ")) != 3:
                del location_details[2]
        for marker in soup.find_all("div",{'class':"marker"}):
            if location_details[3] in list(marker.stripped_strings):
                lat = marker["data-lat"]
                lng = marker["data-lng"]
        for i in range(len(location_details)):
            if "Phone:" in location_details[i]:
                phone = location_details[i].split('Phone:')[1].replace("\xa0","")
                del location_details[i]
                break
        for i in range(len(location_details)):
            if len(location_details[i].split("-")) == 3 and len(location_details[i]) == 12:
                phone = location_details[i]
                del location_details[i]
                break
        for i in range(len(location_details)):
            if "Class Times" in location_details[i]:
                hours = " ".join(location_details[i+1:])
                del location_details[i:]
                break
        store = []
        store.append("https://www.jabzboxing.com")
        store.append(location_details[1])
        store.append(location_details[2])
        store.append(location_details[0].split(",")[0])
        store.append(location_details[0].split(",")[-1].split("–")[0])
        store.append(location_details[3].split(" ")[-1] if len(location_details[3].split(" ")[-1]) == 5 else "<MISSING>")
        if store[-1] == "<MISSING>":
            location_request = session.get(location.find("a",text=re.compile("Visit Website"))["href"],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            store[-1] = location_soup.find("span",{"itemprop":"postalCode"}).text
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("jabz boxing")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        for i in range(len(store)):
            store[i] = store[i].replace("–","-")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
