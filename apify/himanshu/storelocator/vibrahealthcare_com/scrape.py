import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time



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
	addressesess =[]
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
		'accept': '*/*',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
	}
	locator_domain = base_url = "https://www.vibrahealthcare.com"

	r = session.get("https://www.vibrahealthcare.com/locations/",headers=headers)
	soup= BeautifulSoup(r.text,"lxml")
	for link  in soup.find_all("li",class_="item"):
		# print(list(link.find("span",{"class":"address"}).stripped_strings)[0])
		try:
			location_type = link['data-locationclass']
		except:
			location_type ="<MISSING>"
		page_url = "https://www.vibrahealthcare.com/"+link.find("strong",{"class":"name"}).find("a")['href']
		location_name = link.find("strong",{"class":"name"}).text.strip()
		add=list(link.find("span",{"class":"address"}).stripped_strings)
		street_address = list(link.find("span",{"class":"address"}).stripped_strings)[0]
		if street_address=='Lakeway, TX 78734':
			street_address = "2000 Medical Dr."
			location_type ="<MISSING>"
		try:
			city = link['data-city']
		except:
			city=add[-1].split(",")[0]
		try:
			state =link['data-state']
		except:
			state =add[-1].split(",")[1].split( )[0]
		try:
			zipp  =link['data-zip']
		except:
			zipp =add[-1].split(",")[1].split( )[1]
		try:
			country_code = link['data-country']
		except:
			country_code ="<MISSING>"
		store_number="<MISSING>"

		phone =link.find("strong",{"class":"number"}).text.strip()
		hours_of_operation ="<MISSING>"
		try:
			latitude = link['data-latitude']
			longitude = link['data-longitude']
		except:
			latitude ="<MISSING>"
			longitude ="<MISSING>"
		# soup_loc.find("div",class_="location-info")['data-latitude']
		store =[]
		store = [locator_domain, location_name, street_address, city, state, zipp, "US",
			 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
		if store[2] in addressesess:
			continue
		addressesess.append(store[2])
		yield store
		# print("data = " + str(store))
		# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
		

	



def scrape():
	data = fetch_data()
	write_output(data)

scrape()
