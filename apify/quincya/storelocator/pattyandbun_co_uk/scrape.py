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
	
	base_link = "https://www.pattyandbun.co.uk/locations-and-menus"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	data = []

	items = base.find_all(class_="div-block-860")
	locator_domain = "pattyandbun.co.uk"

	for item in items:

		link = "https://www.pattyandbun.co.uk" + item.a["href"]
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = item.text.strip()

		street_address = base.find(id="address").text.strip()
		city_line = base.find(class_="heading-41").text.strip().split(" ")
		city = " ".join(city_line[:-2]).strip().replace("o","O")
		if "," in city:
			street_address = street_address + " " + city.split(",")[0]
			city = city.split(",")[1].strip()
		state = "<MISSING>"
		zip_code = " ".join(city_line[-2:]).strip()
		country_code = "GB"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone = base.find(class_="rich-text-block-6 w-richtext").a.text.strip()
			if "@" in phone:
				phone = base.find(class_="rich-text-block-6 w-richtext").find_all("a")[1].text.strip()
		except:
			phone = "<MISSING>"

		hours_of_operation = base.find(class_="rich-text-block-3 w-richtext").text.replace("day","day ").replace("am","am ").replace("pm","pm ").replace("PM","PM ").replace("â\x80\x93","").replace("â\x80\x8d","").strip()
		if "*" in hours_of_operation:
			hours_of_operation = hours_of_operation[:hours_of_operation.find("*")].strip()
		if "We" in hours_of_operation:
			hours_of_operation = hours_of_operation[:hours_of_operation.find("We")].strip()
		if "Please" in hours_of_operation:
			hours_of_operation = hours_of_operation[:hours_of_operation.find("Please")].strip()

		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

		try:
			map_link = base.find(class_="button-23 w-button")["href"]
			at_pos = map_link.rfind("!3d")
			latitude = map_link[at_pos+3:map_link.rfind("!")].strip()
			longitude = map_link[map_link.find("!4d", at_pos)+3:].strip()
			if len(latitude) > 30:
				latitude = map_link[map_link.find("=")+1:map_link.find(",")].strip()
				longitude = map_link[map_link.find(",")+1:map_link.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
