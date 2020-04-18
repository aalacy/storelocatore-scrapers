import csv
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
import json
import phonenumbers
session = SgRequests()
def write_output(data):
	with open('data.csv', mode='w',newline="") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    base_url="https://www.steward.org/"
    r = session.get("https://www.steward.org/network/our-hospitals",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for data in soup.find_all("div",{"col-md-4 col-sm-6 col-xs-12 state-location"}):
        location_name = data.find("h3").text
        addr = list(data.find("div",{"class":"state-location-left"}).find("div").stripped_strings)
        street_address = addr[1]
        city = addr[-1].split(",")[0]
        state = addr[-1].split(",")[-1].split()[0]
        zipp = addr[-1].split(",")[-1].split()[1]
        phone = phonenumbers.format_number(phonenumbers.parse(str(data.find("a",{"class":"phone"})['href'].replace("tel:","")), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
        page_url = data.find("a",{"class":"website"})['href']
        store =[]
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("HOSPITAL")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

        yield store
    
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
