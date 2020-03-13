import csv
import sys
import requests
from bs4 import BeautifulSoup
import re
import json



def write_output(data):
    with open('data.csv', mode='w',newline= "") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    locator_domain = "https://allsups.com/"
    addresses = []
    for no in range(1,500):
        #print(no)
        page_url = "https://allsups.com/locations/details/"+str(no)
        r= requests.get(page_url,headers= headers)
        soup = BeautifulSoup(r.text,"lxml")
        location_name = soup.find("h1",class_="hTitle").text.strip()
        if location_name == "":
            # print("----")
            continue
        store_number = location_name.split()[-1].strip()
        street_address = soup.find("span",class_="street-address").text.strip()
        city = soup.find("span",class_="locality").text.strip()
        state = soup.find("abbr",class_="region").text.strip()
        zipp_tag = soup.find("span",class_="postal-code").text.strip()
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp_tag))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp_tag))
        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"
        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        phone = soup.find("div",class_="tel").text.strip()
        location_type = "<MISSING>"
        latitude = soup.findAll("script",text = re.compile("generateMap"))[-1].text.split("(")[1].split(")")[0].split(",")[0].strip()
        longitude = soup.findAll("script",text = re.compile("generateMap"))[-1].text.split("(")[1].split(")")[0].split(",")[1].strip()
        hours_of_operation = "<MISSING>"
        if street_address in addresses:
            continue
        addresses.append(street_address)
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else "<MISSING>")
        yield store
        # print("===========",store)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
