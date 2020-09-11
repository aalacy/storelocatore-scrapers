from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.shakeshack.co.uk/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	data = []

	items = base.find_all(class_="c-location")
	locator_domain = "shakeshack.co.uk"

	for item in items:

		location_name = item.a.text.strip()
		link = item.a["href"]

		city = ""
		raw_address = item.p.text.split("\n")
		zip_code = raw_address[3].replace(",","")
		if len(zip_code) > 10:
			zip_code = raw_address[2].replace(",","").strip()
		if zip_code.count(" ") > 1:
			city =  zip_code[:zip_code.find(" ")].strip()
			zip_code = zip_code[zip_code.find(" ")+1:].strip()

		address_text = item.p.text
		if city:
			street_address = address_text[:address_text.find(city)].strip()
		else:
			for i, row in enumerate(raw_address):
				if zip_code in row:
					city = raw_address[i-1].strip()
					street_address = " ".join(raw_address[:i-1])

		if "," in city:
			street_address = street_address + " " + city[:city.find(",")].strip()
			city = city[city.find(",")+1:].strip()

		if street_address[-1:] == ",":
			street_address = street_address[:-1]
		street_address = street_address.replace("\n"," ").replace("–","-").strip()
		state = "<MISSING>"
		country_code = "GB"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone =  re.findall("[\d]{5} [\d]{3} [\d]{3}", str(item).replace("0192 3886","01923 886"))[0]
		except:
			phone = "<MISSING>"

		try:
			hours_of_operation = item.find_all("p")[1].text.replace("\n"," ").replace("–","-")[5:].strip()
			if len(hours_of_operation) < 20:
				hours_of_operation = "<MISSING>"
		except:
			hours_of_operation = "<MISSING>"
		latitude = item.find(class_="marker")["data-lat"]
		longitude = item.find(class_="marker")["data-lng"]

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
