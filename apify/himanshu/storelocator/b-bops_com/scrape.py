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
    base_url = "https://b-bops.com"
    r = session.get("https://b-bops.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "var locations = " in script.text:
            location_list = script.text.split("var locations = ")[1].split("];")[0].split("],")[:-1]
            for store_data in location_list:
                location_details = store_data.replace("[","").strip().replace("\t"," ").replace("\r"," ").split("+")
                location_url = BeautifulSoup(location_details[0],"lxml").find("a")["href"]
                name = BeautifulSoup(location_details[1],"lxml").text
                street_address = BeautifulSoup(location_details[2],"lxml").text
                address_2 = BeautifulSoup(location_details[3],"lxml").text.strip()
                phone = BeautifulSoup(location_details[4].split(",")[0],"lxml").text.replace("'","")
                location_request = session.get("https://b-bops.com/" + location_url,headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                hours = " ".join(list(location_soup.find("table",{'class':"table"}).stripped_strings))
                store = []
                store.append("https://b-bops.com")
                store.append(name.strip())
                store.append(street_address.strip())
                store.append(address_2.split(",")[0].replace("'",""))
                store.append(address_2.split(",")[1].split(" ")[-2])
                store.append(address_2.split(",")[1].split(" ")[-1].replace("'",""))
                store.append("US")
                store.append(location_url.split("/")[-1])
                store.append(phone)
                store.append("b-bop's")
                store.append(location_details[4].split(",")[-2])
                store.append(location_details[4].split(",")[-1].replace("']",""))
                store.append(hours if hours != "" else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
