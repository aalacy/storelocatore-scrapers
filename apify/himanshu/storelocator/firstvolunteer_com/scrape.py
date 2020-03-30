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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.firstvolunteer.com"
    r = session.get("https://www.firstvolunteer.bank/locations/",headers=headers,verify=False)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("li",{'class':"bank_menu_li_li vtip"}):
        location_request = session.get("https://www.firstvolunteer.bank/locations/bank-branch/" + location["slug"] + "/",headers=headers,verify=False)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{"class":"branch_col_2"}).stripped_strings)
        for i in range(len(location_details)):
            if "Hours" in location_details[i]:
                hours = " ".join(location_details[i:])
                break
        geo_location = location_soup.find("div",{"class":"branch_col_2"}).find("a")["href"]
        store = []
        store.append("https://www.firstvolunteer.com")
        store.append(location_details[0])
        store.append(location_details[1])
        if len(location_details[2].split(",")) == 1:
            store.append(" ".join(location_details[2].split(" ")[:-2]))
            store.append(location_details[2].split(" ")[-2])
            store.append(location_details[2].split(" ")[-1])
        else: 
            store.append(location_details[2].split(",")[0])
            store.append(location_details[2].split(",")[1].split(" ")[-2])
            store.append(location_details[2].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[4].split(" | Phone")[0])
        store.append("first volunteer bank")
        store.append(geo_location.split("daddr=")[1].split(",")[0])
        store.append(geo_location.split("daddr=")[1].split(",")[1])
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
