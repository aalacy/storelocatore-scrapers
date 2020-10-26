import csv
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup
import re



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
	locator_domain = "https://www.expresscare.com/"
	addresses=[]
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
		'accept': '*/*',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
	}
	r= session.get("http://locations.expresscare.com/",headers=headers)
	soup = BeautifulSoup(r.text,"lxml")
	for state_url in soup.find_all("div",class_="itemlist"):
		# print(state_url.find("a").text)
		r1 = session.get(state_url.find("a")["href"],headers=headers)
		soup1 = BeautifulSoup(r1.text,"lxml")
		for city_url in soup1.find_all("div",class_="itemlist"):
			r2 = session.get(city_url.find("a")["href"],headers=headers)
			soup2 = BeautifulSoup(r2.text,"lxml")
			page_url = soup2.find("div",class_="itemlist_fullwidth").find("a")["href"]
			store_number = page_url.split("/")[-2]
			state = page_url.split("/")[3].upper().strip()
			r3 = session.get(page_url,headers=headers)
			soup3 = BeautifulSoup(r3.text,"lxml")
			location_name = soup3.find("meta",{"property":"og:title"})["content"].capitalize()
			street_address = soup3.find("meta",{"property":"business:contact_data:street_address"})["content"]
			city = soup3.find("meta",{"property":"business:contact_data:locality"})["content"]
			# state = soup3.find("meta",{"property":"business:contact_data:region"})["content"]
			zipp = soup3.find("meta",{"property":"business:contact_data:postal_code"})["content"]
			country_code = soup3.find("meta",{"property":"business:contact_data:country_name"})["content"]
			phone = soup3.find("meta",{"property":"business:contact_data:phone_number"})["content"]
			location_type = "Valvoline express care"
			latitude = soup3.find("meta",{"property":"place:location:latitude"})["content"]
			longitude = soup3.find("meta",{"property":"place:location:longitude"})["content"]
			hour_list = list(soup3.find("div",class_="hours").stripped_strings)
			if "verifyHours" in hour_list[-2]:
				del hour_list[-2]
			hours_of_operation =" ".join(hour_list).replace("Hours","").strip()
			store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
					store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
			store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
			if store[-1] in addresses:
				continue
			addresses.append(store[-1])
			# print("data = " + str(store))
			# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
			yield store

def scrape():
	data = fetch_data()
	write_output(data)
scrape()
