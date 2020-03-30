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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://f45training.com"
    r = session.get("https://f45training.com/find-a-studio/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []

    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "window.domains" in script.text:
            location_list = json.loads(script.text.split("window.studios = ")[1].split("}]};")[0] + "}]}")["hits"]
            for i in range(len(location_list)):
                current_store = location_list[i]
                store = []
                store.append("https://f45training.com")
                store.append(current_store["name"])
                print(current_store["slug"])
                if current_store["location"] == "":
                    continue
                if current_store["country"] == "United States":
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("US")
                elif current_store["country"] == "Canada":
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("CA")
                else:
                    continue
                store.append(current_store["id"])
                location_request = session.get("https://f45training.com/" + current_store["slug"],headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                if location_soup.find("a",{"href":re.compile('tel:')}) == None:
                    phone = "<MISSING>"
                else:
                    phone = location_soup.find("a",{"href":re.compile('tel:')}).text
                print(phone)
                store.append(phone.split("/")[0].split(",")[0].replace("(JF45)","") if phone != "" else "<MISSING>")
                store.append("f45")
                store.append(current_store["_geoloc"]["lat"])
                store.append(current_store["_geoloc"]["lng"])
                store.append("<MISSING>")
                store.append(current_store["location"])
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
