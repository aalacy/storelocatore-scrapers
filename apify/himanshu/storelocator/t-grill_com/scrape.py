import csv
from bs4 import BeautifulSoup
import re
import json
import time
from sgrequests import SgRequests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_url = "https://t-grill.com/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

    location_url = "https://t-grill.com/locations"
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    add = soup.find("div",{"data-ux":"ContentCards"}).find_all("div",{"data-typography":"BodyAlpha"})

    for i in add:

        temp = i.text
        # print(temp)
        addr = temp.split(",")
        # print(addr)

        tt = addr[1].split(" ")[2:]
    
        new_tt = [i.replace(u'\xa0', u' ') for i in tt]
    
        if len(new_tt) == 3:
            part1 = " ".join(new_tt[:2])
        else:
            part1= " ".join(new_tt[:3])

        part2 = new_tt[-1].split(" ")
        part22 = part2[0]
        street_address = part1 + " " + part22
        phone = part2[1]
        city = addr[0]
        state = addr[1].split(" ")[1]
        location_name = "Teriyaki Grill - " + city


        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append("<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("Restaurant")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(location_url)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
