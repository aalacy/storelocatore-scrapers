# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


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
    base_url = "http://4sonsstores.com"
    r = session.get(base_url + "/2-top-tier-fuel.html")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    stores_map = soup.find("map",{"name": "Map"})
    for area in stores_map.find_all("area"):
        store = []
        store_id = area["href"]
        store_request = session.get(base_url + "/" + str(store_id))
        store_soup = BeautifulSoup(store_request.text,"lxml")
        table = store_soup.find("table",{"style": "width: 559px; height: 55px;"})
        temp_var = []
        for td in table.find_all("td"):
            temp_var.extend(list(td.stripped_strings))
        temp_var = [value for value in temp_var if value != "Â"]
        if "(" in temp_var[3] and ")" not in temp_var[3]:
            temp_address = ""
            temp_number = 3
            for i in range(3,len(temp_var)):
                temp_address = temp_address + temp_var[i]
                temp_number = temp_number + 1
                if ")" in temp_var[i]:
                    break
            del temp_var[3:temp_number]
            temp_var.insert(3,temp_address)
        if "(" not in temp_var[3] and ")" not in temp_var[3]:
            if "(" in temp_var[4] and ")" not in temp_var[4]:
                temp_address = ""
                temp_number = 4
                for i in range(4,len(temp_var)):
                    temp_address = temp_address + temp_var[i]
                    temp_number = temp_number + 1
                    if ")" in temp_var[i]:
                        break
                del temp_var[3:temp_number]
                temp_var.insert(3,temp_address)
            elif "(" in temp_var[4] and ")" in temp_var[4]:
                del temp_var[3]
            elif "(" not in temp_var[4] and ")" not in temp_var[4]:
                temp_var[2:5] = [' '.join(temp_var[2:5])]
        if len(temp_var) == 10:
            temp_var[4:7] = [' '.join(temp_var[4:7])]
        store.append("http://4sonsstores.com")
        store.append(temp_var[2])
        store.append(temp_var[4])
        store.append(temp_var[5].split(',')[0])
        store.append(temp_var[5].split(",")[1].split(" ")[1].replace("Â"," "))
        store.append(temp_var[5].split(",")[1].split(" ")[2])
        store.append("US")  
        store.append(temp_var[1].split("#")[1])
        store.append(temp_var[6].split("PHONE:")[1])
        store.append("4sonsstores")
        store.append(store_soup.find("a",text="View Larger Map")['href'].split("&ll=")[1].split(",")[0])
        store.append(store_soup.find("a",text="View Larger Map")['href'].split("&ll=")[1].split(",")[1].split("&")[0])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
