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
    base_url = "http://quicklyusa.com"
    r = session.get("http://quicklyusa.com/quicklystores.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    addresses = []
    for location in soup.find_all("table")[2].find_all("a")[:-1]:
        if location.text == "":
            continue
        location_request = session.get(base_url + "/" + location["href"])
        location_soup = BeautifulSoup(location_request.text,"lxml")
        iframe = location_soup.find("iframe")["src"]
        geo_request = session.get(iframe,headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                try:
                    geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                    lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                    lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
                except:
                    geo_data = "<MISSING>"
                    lat = "<MISSING>"
                    lng = "<MISSING>"
        store = []
        store.append("http://quicklyusa.com")
        store.append(location.text)
        if geo_data == "<MISSING>":
            store.append(list(location_soup.find("font",{'face':"arial, helvetica"}).stripped_strings)[0].split("(")[0])
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
        else:
            store.append(" ".join(geo_data.split(",")[0:-2]) if " ".join(geo_data.split(",")[0:-2]) != "" else "<MISSING>")
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(geo_data.split(",")[-2])
            store.append(geo_data.split(",")[-1].split(" ")[1])
            store.append(geo_data.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("quicklyusa")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        return_main_object.append(store)
    r = session.get("http://quicklyusa.com/otqulo.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("table")[2].find_all("a")[:-1]:
        if location.text == "":
            continue
        location_request = session.get(base_url + "/" + location["href"])
        location_soup = BeautifulSoup(location_request.text,"lxml")
        iframe = location_soup.find("iframe")["src"]
        geo_request = session.get(iframe,headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                try:
                    geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                    lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                    lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
                except:
                    geo_data = "<MISSING>"
                    lat = "<MISSING>"
                    lng = "<MISSING>"
        store = []
        store.append("http://quicklyusa.com")
        store.append(location.text)
        if geo_data == "<MISSING>":
            store.append(list(location_soup.find("font",{'face':"arial, helvetica"}).stripped_strings)[0].split("(")[0])
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
        else:
            store.append(" ".join(geo_data.split(",")[0:-2]) if " ".join(geo_data.split(",")[0:-2]) != "" else "<MISSING>")
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(geo_data.split(",")[-2])
            store.append(geo_data.split(",")[-1].split(" ")[1])
            store.append(geo_data.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("quicklyusa")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
