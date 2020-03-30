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
    base_url = "https://www.oritani.com"
    r = session.get("https://www.oritani.com/Locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_list = soup.find_all("div",{"class":"col-sm-12 col-md-6"})
    for i in range(0,len(location_list),2):
        if location_list[i+1].find("a") == None:
            lat = "<MISSING>"
            lng = "<MISSING>"
        else:
            lat = location_list[i+1].find("a")["href"].split("/@")[1].split(",")[0]
            lng = location_list[i+1].find("a")["href"].split("/@")[1].split(",")[1]
        location_details = list(location_list[i].stripped_strings)
        if location_details[3] == "Phone":
            location_details[3] = "".join(location_details[3:5])
            del location_details[4]
        store = []
        store.append("https://www.oritani.com")
        store.append(location_details[0])
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store.append(",".join(location_details[2].split(",")[1:]).split(" ")[-2].replace(",",""))
        store.append(",".join(location_details[2].split(",")[1:]).split(" ")[-1].replace(",",""))
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[3].split("Phone:")[1])
        store.append("oritani bank")
        store.append(lat)
        store.append(lng)
        store.append(" ".join(location_details[4:]))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
