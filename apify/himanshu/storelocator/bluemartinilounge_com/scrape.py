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
    base_url = "https://bluemartinilounge.com"
    r = requests.get("https://bluemartinilounge.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("ul",{'class':"loc-slide"}).find_all("a"):
        location_request = requests.get("https:" + location["href"] + "contact/",headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = list(location_soup.find("div",{'class':"cont-align-bottom"}).find("p").stripped_strings)[0]
        address = list(location_soup.find("div",{'class':"cont-align-bottom"}).stripped_strings)
        main_address = ""
        for i in range(len(address)):
            if address[i] == "Call:":
                main_address = address[i+1:i+3]
        if main_address == "":
            for i in range(len(address)):
                if address[i] == "Contact:":
                    for j in range(len(address)):
                        if "Call/" in address[j]:
                            main_address = [address[j+1],address[i+2]]
        if main_address == "":
            phone = location_soup.find("a",{"href":re.compile("tel:")}).text
            main_address = [phone,location_soup.find_all("p",{'class':"f30"})[1].text]
        for i in range(len(address)):
            if address[i] == "Hours of Operation:":
                hours = address[i+1]
        store = []
        store.append("https://bluemartinilounge.com")
        store.append(name)
        store.append(" ".join(main_address[1].split(",")[0:-2]))
        store.append(main_address[1].split(",")[-2])
        store.append(main_address[1].split(",")[-1].split(" ")[-2])
        store.append(main_address[1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(main_address[0])
        store.append("blue martini")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
