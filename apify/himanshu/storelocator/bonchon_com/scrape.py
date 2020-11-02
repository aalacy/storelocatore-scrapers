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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    base_url = "https://bonchon.com"
    r = session.get(base_url+"/locations-menus",headers=header)
    soup = BeautifulSoup(r.text,"lxml")
    scripts = soup.find_all("script")
    return_main_object = []
    scripts = soup.find_all("script")
    for script in scripts:
        if "var locations" in script.text:
            location_list = json.loads(script.text.split("var locations = ")[1].split("];")[0] + "]")
            for i in range(len(location_list)):
                if location_list[i] == None:
                    continue
                store_data = location_list[i]
                store = []
                location_reqeust = session.get(store_data["permalink"],headers=header)
                location_soup = BeautifulSoup(location_reqeust.text,"lxml")
                store.append("https://bonchon.com")
                store.append(store_data['title'])
                store.append("<INACCESSIBLE>")
                store.append("<INACCESSIBLE>")
                if len(store_data['address_entered'].split(",")[-1].split(" ")) > 3 and len(store_data['address_entered'].split(",")[-1].split(" ")[-1]) != 5:
                    store.append(store_data['address_entered'].split(",")[-1].split(" ")[-3])
                    store.append(store_data['address_entered'].split(",")[-1].split(" ")[-2].strip())
                else:
                    store.append(store_data['address_entered'].split(",")[-1].split(" ")[-2].strip())
                    store.append(store_data['address_entered'].split(",")[-1].split(" ")[-1].strip())
                if store[-1] == "#":
                    store[-1] = store_data['address_entered'].split(",")[-1].split(" ")[2].strip()
                if "\ufeff" in store[-1]:
                    store[-1] = store[-1].split("\ufeff")[0]
                if store[-2] == "(Suite":
                    store[-2] = store_data['address_entered'].split(",")[-1].split(" ")[1].strip()
                if store[-2] == "Suite":
                    store[-2] = store_data['title'].split(",")[-1]
                if "#" in store[-1]:
                    store[-1] = store_data['address'].split(",")[-1].split(" ")[-1].strip()
                if store[-2] == "":
                    store[-2] = store[1].split(",")[1]
                store.append("US")
                store.append("<MISSING>")
                phone = location_soup.find("div",{"class":"store-phone"}).text.strip()
                phone = phone.split("&")[0].split("/")[0].split("and")[0]
                hours = " ".join(list(location_soup.find("div",{"class":"opening-hours"}).stripped_strings))
                store.append(phone if phone != "" else "<MISSING>")
                store.append("bon chon")
                store.append(store_data["lat"])
                store.append(store_data["lng"])
                store.append(hours if hours != "" else "<MISSING>")
                store.append(store_data["address_entered"].replace("\ufeff",""))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
