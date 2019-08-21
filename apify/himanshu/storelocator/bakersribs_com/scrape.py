import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

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
    base_url = "http://bakersribs.com"
    r = requests.get("http://bakersribs.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("div",{'id':"recent-posts-2"}).find_all("a"):
        location_request = requests.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{'class':"et_pb_blurb_description"}).stripped_strings)
        geo_request = requests.get(location_soup.find("iframe",{'src':re.compile("google")})["src"],headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
        for i in range(len(location_details)):
            if "Phone:" == location_details[i]:
                phone = location_details[i+1]
            elif "Phone:" in location_details[i]:
                phone = location_details[i].split("Phone:")[1]
        for i in range(len(location_details)):
            if "HOURS" == location_details[i]:
                hours = " ".join(location_details[i+1:])
        store = []
        store.append("http://bakersribs.com")
        store.append(location.text)
        store.append(geo_data.split(",")[1])
        store.append(geo_data.split(",")[2])
        store.append(geo_data.split(",")[-1].split(" ")[-2])
        store.append(geo_data.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.replace("\xa0",""))
        store.append("baker's ribs")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
