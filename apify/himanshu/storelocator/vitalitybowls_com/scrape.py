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
    base_url = "https://vitalitybowls.com"
    r = session.get("https://vitalitybowls.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_links = []
    for states in soup.find_all("div",{"class":'et_pb_text_inner'}):
        for link in states.find_all("a"):
            print(link["href"])
            if link["href"] in location_links:
                continue
            location_links.append(link["href"])
            location_request = session.get(link["href"],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            name = location_soup.find("h2",{"class":"et_pb_slide_title"}).text
            address = list(location_soup.find("div",{"class":'et_pb_column et_pb_column_1_4 et_pb_column_inner et_pb_column_inner_0'}).find("div",{"class":"et_pb_text_inner"}).stripped_strings)
            hours = " ".join(list(location_soup.find("div",{"class":"et_pb_column et_pb_column_1_4 et_pb_column_inner et_pb_column_inner_1"}).stripped_strings))
            phone_details = list(location_soup.find_all("div",{"class":'et_pb_text_inner'})[3].stripped_strings)
            geo_location = location_soup.find("iframe")["src"]
            if "coming soon" in " ".join(phone_details).lower():
                continue
            phone = ""
            phone_details = [x.lower() for x in phone_details]
            for k in range(len(phone_details)):
                if "tel:" in phone_details[k]:
                    phone = phone_details[k].split("tel:")[1].replace("email:","")
                    if phone == "":
                        phone = phone_details[k+1]
            if phone == "":
                for k in range(len(phone_details)):
                    if "phone:" in phone_details[k]:
                        if k == len(phone_details) - 1 or "email" in phone_details[k+1]:
                            phone = phone_details[k].split("phone:")[1].replace("\xa0"," ")
                        else:
                            phone = phone_details[k+1].replace("email:","")
                            if phone == "":
                                phone = phone_details[k].split("phone:")[1]
            store = []
            store.append("https://vitalitybowls.com")
            store.append(name)
            if "(" in address[-1] or ")" in address[-1] or "building." in address[-1]:
                store.append(address[1])
                store.append(address[-2].split(" ")[0].replace(","," "))
                store.append(address[-2].split(" ")[-2])
                store.append(address[-2].split(" ")[-1])
            else:
                store.append(" ".join(address[1:-1]))
                if len(address[-1].split(" ")) == 2:
                    store.append(" ".join(address[-1].split(" ")[0:-2]).replace(","," "))
                    store.append(address[-1].split(" ")[-1])
                    store.append("<MISSING>")
                else:
                    store.append(" ".join(address[-1].split(" ")[0:-2]).replace(","," "))
                    store.append(address[-1].split(" ")[-2])
                    store.append(address[-1].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("vitality bowls")
            if "!3d" in geo_location and "!2d" in geo_location:
                store.append(geo_location.split("!3d")[1].split("!")[0])
                store.append(geo_location.split("!2d")[1].split("!")[0])
            else:
                store.append("<INACCESSIBLE>")
                store.append("<INACCESSIBLE>")
            store.append(hours)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
