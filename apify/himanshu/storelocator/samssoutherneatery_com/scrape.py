import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://samssoutherneatery.com"
    r = requests.get("https://samssoutherneatery.com/locations-list",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for a in soup.find("main",{"class":"Index"}).find_all("a"):
        if a.find("strong") == False or a["href"][0] != "/":
            continue
        location_request = requests.get(base_url + a["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        address = list(location_soup.find("div",{'class':"sqs-block-content"}).find("p").stripped_strings)
        name = location_soup.find("div",{'class':"sqs-block-content"}).find("h2").text.strip()
        zip_split =  re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",address[1])
        store_zip = zip_split[0]
        state_split = re.findall("([A-Z]{2})",address[1])
        if state_split:
            state = state_split[-1]
        else:
            state = "<MISSING>"
        if location_soup.find("div",{'class':"sqs-block-content"}).find("a",{"href":re.compile("tel:")}):
            phone = location_soup.find("div",{'class':"sqs-block-content"}).find("a",{"href":re.compile("tel:")}).text
        else:
            phone = "<MISSING>"
        store = []
        store.append("http://samssoutherneatery.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.strip() if phone else "<MISSING>")
        store.append("<MISSING>")
        geo_object = json.loads(location_soup.find("div",{"data-block-json":re.compile("")})["data-block-json"])["location"]
        store.append(geo_object["markerLat"])
        store.append(geo_object["markerLng"])
        hours_url = location_soup.find_all("a",text="Order Now")[-1]["href"]
        print(hours_url)
        hours_request = requests.get(hours_url,headers=headers)
        hours_soup = BeautifulSoup(hours_request.text,"lxml")
        hours = " ".join(list(hours_soup.find("div",{'id':'home-hours'}).stripped_strings))
        if "Monday - Sunday Closed" in hours:
            continue
        store.append(hours if hours else "<MISSING>")
        store.append(base_url + a["href"])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
