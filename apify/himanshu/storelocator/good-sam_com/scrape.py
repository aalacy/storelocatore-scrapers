import csv
from sgrequests import SgRequests
import json
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
    locator_domain = "https://www.good-sam.com/"
    addresses = []
    country_code = "US"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    r = session.get("https://www.good-sam.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")

    for links in  soup.find("map",{"id":"usa"}).find_all("area"):
        link = "https://www.good-sam.com/locations"+links["href"]
        r1 = session.get(link,headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        loc = json.loads(soup1.find("div",class_="location-google-map")["data-locations"])
        for x in loc:
            store_number = x["entry_id"]
            location_name = x["title"]
            latitude = x["latitude"]
            longitude = x["longitude"]
            state = x["location_state"]
            city = x["location_city"]
            phone = x["location_phone"]
            page_url ="https://www.good-sam.com"+ x["url"]
            r2 = session.get(page_url,headers=headers)
            soup2 = BeautifulSoup(r2.text,"lxml")
            try:
                address =" ".join(list(soup2.find("div",class_="page-header-meta").find("address").stripped_strings)).split(",")
                street_address = " ".join(address[:-2]).encode('ascii', 'ignore').decode('ascii').strip()
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[-1]))
                if us_zip_list:
                    zipp=us_zip_list[0]
                else:
                    zipp="<MISSING>"
            except:
                street_address="<MISSING>"
                zipp="<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            if "Serving the communities of Brainerd and Pine River" in city:
                city = "Pine River"
            if  "Providing senior care and services in Greeley" in city:
                city = "Greeley"
            if "Serving the communities of Prescott and Prescott Valley" in city :
                city = "Prescott Valley"
            if "Serving the community of Luverne" in city:
                city = "Luverne"
            if "Serving Hastings" in city:
                city = "Hastings"
            if "Serving the community of Albion" in city:
                city = "Albion"
            if "Serving the community of Valentine" in city:
                city = "Valentine"
            if "Providing senior care and services in and around Sioux Falls" in city:
                city="Sioux Falls"
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
