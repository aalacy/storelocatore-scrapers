import csv
from bs4 import BeautifulSoup
import re
import json
import requests
from sgrequests import SgRequests
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    r =  session.get("https://cnbrown.com/big-apple/contact-us/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")   
    links = soup.find_all("script",{"type":"text/javascript"})[7].text.split('","locations":"')[1].split("/* ]]> */")[0].replace('}]"};','}]').replace("\\","")
    json_data = json.loads(links)
    for i in json_data:
        store = []
        store.append("https://cnbrown.com")
        store.append(i['title'])
        store.append(i['address'])
        store.append(i['city'])
        store.append(i['state'])
        store.append(i['zip'])
        store.append("US")
        store.append(i['id'])
        store.append(i['phone'])
        store.append("<MISSING>")
        store.append(i['lat'])
        store.append(i['long'])
        store.append("<MISSING>")
        store.append("https://cnbrown.com/big-apple/contact-us/")
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
