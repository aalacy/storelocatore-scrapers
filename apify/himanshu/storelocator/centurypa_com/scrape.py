import csv
from sgrequests import SgRequests
# import json
# from datetime import datetime
# import phonenumbers
from bs4 import BeautifulSoup
import re
# import unicodedata
# import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv',newline="", mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = "https://www.centurypa.com/"
    addresses = []
    country_code = "US"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    r = session.get("https://www.centurypa.com/communities/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for statelinks in soup.find("div",{"id":"stateListContain"}).find_all("a"):
        # print(statelinks.text)
        r1 = session.get("https://www.centurypa.com"+statelinks["href"],headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        for loc_contain in soup1.find("div",{"id":"locationContain"}).find_all("div",class_="locationDeets"):
            location_name = loc_contain.find("h2").text.strip()
            page_url = "https://www.centurypa.com"+loc_contain.find("h2").a["href"]
            phone = loc_contain.find("p",class_="lrgPhone").text.replace("Phone:","").strip()
            address = list(loc_contain.find("p",class_="lrgPhone").find_next("p").stripped_strings)
            street_address = " ".join(address[:-1]).strip()
            city = address[-1].split(",")[0].strip()
            state = address[-1].split(",")[-1].split()[0].strip()
            zipp = address[-1].split(",")[-1].split()[-1].strip()
            # print(street_address+" | "+city+" | "+state+" | "+zipp)
            r3 = session.get(page_url,headers=headers)
            soup3 = BeautifulSoup(r3.text,"lxml")
            contact_link = "https://www.centurypa.com"+soup3.find("div",class_="contactContain").find("a",class_="ghostBtn")["href"]
            r4 = session.get(contact_link,headers=headers)
            soup4 = BeautifulSoup(r4.text,"lxml")
            longitude = soup4.find("div",{"id":"map"}).find("iframe")["src"].split("!2d")[1].split("!3d")[0]
            latitude = soup4.find("div",{"id":"map"}).find("iframe")["src"].split("!2d")[1].split("!3d")[1].split("!")[0]
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

           # print("data = " + str(store))
           # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


       


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
