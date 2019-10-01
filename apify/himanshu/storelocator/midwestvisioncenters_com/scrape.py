import csv
import requests
from bs4 import BeautifulSoup
import re
import json

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
    base_url = "https://www.midwestvisioncenters.com"
    r = requests.get("https://www.midwestvisioncenters.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for sub_menu in soup.find("span",text="Locations").parent.parent.find_all("ul",{"class":"sub-menu"}):
        if sub_menu.find("ul",{"class":"sub-menu"}) == None:
            continue
        for link in sub_menu.find("ul",{"class":"sub-menu"}).find_all("a"):
            print(link["href"])
            location_reqeust = requests.get(link["href"],headers=headers)
            location_soup = BeautifulSoup(location_reqeust.text,"lxml")
            location_details = []
            for k in range(len(location_soup.find_all("h5",{'style':"text-align: center;"}))):
                location_details.extend(list(location_soup.find_all("h5",{'style':"text-align: center;"})[k].stripped_strings))
                if len(location_details[0]) < 10:
                    location_details[0] = " ".join(location_details[0:2])
                    del location_details[1]
            print(location_details[0:6])
            store = []
            store.append("https://www.midwestvisioncenters.com")
            store.append(link["href"].split("/")[-2])
            if len(location_details[0].split(",")) == 3:
                store.append(location_details[0].split(",")[0])
                store.append(location_details[0].split(",")[1])
                store.append(location_details[0].split(",")[-1].split(" ")[-2])
                store.append(location_details[0].split(",")[-1].split(" ")[-1])
            elif len(location_details[0].split("\xa0")) > 1:
                if location_details[0].count("\xa0") == 4:
                    store.append(location_details[0].split("\xa0")[0])
                    store.append(location_details[0].split(",")[1].replace("\xa0"," "))
                    store.append(location_details[0].split(",")[2])
                    store.append(location_details[0].split("\xa0")[-1])
                else:
                    store.append(location_details[0].split("\xa0")[0])
                    store.append(location_details[0].split("\xa0")[-1].split(",")[0])
                    store.append(location_details[0].split("\xa0")[-1].split(",")[-1].split(" ")[-2])
                    store.append(location_details[0].split("\xa0")[-1].split(",")[-1].split(" ")[-1])
            elif len(location_details[0].split(",")) == 4:
                store.append(" ".join(location_details[0].split(",")[0:-2]))
                store.append(location_details[0].split(",")[2])
                store.append(location_details[0].split(",")[-1].split(" ")[-2])
                store.append(location_details[0].split(",")[-1].split(" ")[-1])
            else:
                store.append(location_details[1])
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            phone = ""
            for k in range(len(location_details[0:5])):
                if "Phone" == location_details[k]:
                    phone = location_details[k+1]
                elif "Phone" in location_details[k]:
                    phone = location_details[k].split("\xa0")[0].split("Phone")[1].strip()
                    if phone == "":
                        phone = location_details[k].split("\xa0")[1]
            store.append(phone if phone!= "" else "<MISSING>")
            store.append("midwest vision centers")
            geo_location = location_soup.find_all("iframe")[-1]["src"]
            if "!2d" in geo_location and "!3d" in geo_location:
                store.append(geo_location.split("!3d")[1].split("!")[0])
                store.append(geo_location.split("!2d")[1].split("!")[0])
            elif "&sll=" in geo_location:
                store.append(geo_location.split("&sll=")[1].split(",")[0])
                store.append(geo_location.split("&sll=")[1].split(",")[0].split("&")[0])
            hours = ""
            print(location_details[0:7])
            for k in range(len(location_details[0:7])):
                if "AM" in location_details[k] or "PM" in location_details[k] or "open" in location_details[k].lower() or "monday" in location_details[k].lower() or "close" in location_details[k].lower() or "Sat" in location_details[k] or "thursday" in location_details[k].lower() or "tuesday" in location_details[k].lower() or "wednesday" in location_details[k].lower() or "friday" in location_details[k].lower() or "sunday" in location_details[k].lower():
                    hours = hours + " " + location_details[k]
            store.append(hours if hours != "" else " ".join(location_details[3:6]).split("Manager:")[0])
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
