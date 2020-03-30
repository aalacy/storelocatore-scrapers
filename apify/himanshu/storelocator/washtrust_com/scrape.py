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
    base_url = "https://www.washtrust.com"
    r = session.get("https://www.washtrust.com/About-Us/Locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if '{"options"' in script.text:
            location_list = json.loads('{"options"' + script.text.split('{"options"')[1].split("}]}]}")[0] + "}]}]}")["markers"]
    for location in soup.find_all("article",{"class":"edn_article edn_clearFix"}):
        name = location.find("h2",{"class":"edn_articleTitle"}).text
        location_url = location.find("a")["href"]
        location_details = location.find("h3").text
        phone = "-".join(location_details.split("-")[1:])
        address = location_details.split("-")[0]
        lat = ""
        lng = ""
        for k in range(len(location_list)):
            if location_list[k]["url"] == location_url:
                lat = location_list[k]["position"]["latitude"]
                lng = location_list[k]["position"]["longitude"]
        location_request = session.get(location_url)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = location_soup.find("article",{"class":"edn_article edn_articleDetails"}).find_all("p")
        hours = ""
        for k in range(len(location_details)):
            temp_hours = " ".join(list(location_details[k].stripped_strings))
            if "hour" in temp_hours.lower():
                hours = hours + " " + temp_hours
        store = []
        store.append("https://www.washtrust.com")
        store.append(name)
        store.append(" ".join(address.split(",")[0:-2]))
        store.append(address.split(",")[-2])
        store.append(address.split(",")[-1].split(" ")[-3])
        store.append(address.split(",")[-1].split(" ")[-2])
        store.append("US")
        store.append(location_url.split("/")[-2])
        store.append(phone)
        store.append("washington trust")
        store.append(lat if lat != "" else "<MISSING>")
        store.append(lng if lat != "" else "<MISSING>")
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
