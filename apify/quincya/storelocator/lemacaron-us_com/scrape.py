from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://lemacaron-us.com/locations"

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

	items = base.find_all(class_="location-links") 
	locator_domain = "lemacaron-us.com"

	lats = []
	for item in items:

		link = "https://lemacaron-us.com" + item.a['href']
		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		if "COMING SOON" in base.h2.text.upper() or "COMING SOON" in base.find(class_="text-fade px-2 mb-2").text.upper():
			continue

		print(link)

		location_name = base.h2.span.text

		raw_address = base.find(class_="text-fade px-2 mb-2").text.strip().split("\n")
		street_address = raw_address[0].strip()
		city = raw_address[1].strip().split(",")[0].strip()
		state = raw_address[1].strip().split(",")[1].strip().split()[0]
		zip_code = raw_address[1].strip().split(",")[1].strip().split()[1]
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = base.find_all(class_="btn btn-sm btn-primary btn-icon")[0].text

		latitude = "<MISSING>"
		longitude = "<MISSING>"
		map_link = base.find_all(class_="btn btn-sm btn-primary btn-icon")[-1]['href']
		if "maps" in map_link:
			req = session.get(map_link, headers = HEADERS)
			time.sleep(randint(1,2))
			try:
				maps = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				print('[!] Error Occured. ')
				print('[?] Check whether system is Online.')

			try:
				raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
				latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
				longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
				if len(latitude) < 5 or latitude+longitude in lats:
					latitude = "<MISSING>"
					longitude = "<MISSING>"
				else:
					lats.append(latitude+longitude)
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"

		hours = base.find(class_="text-fade px-2 mb-3").text.replace("\r\n"," ").strip()
		hours_of_operation = (re.sub(' +', ' ', hours)).strip()

		if "(" in hours_of_operation:
			hours_of_operation = hours_of_operation[:hours_of_operation.find("(")].strip()
		if not hours_of_operation or "click" in hours_of_operation.lower():
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
