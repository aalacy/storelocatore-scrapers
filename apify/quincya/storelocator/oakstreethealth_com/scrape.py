from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
from sgselenium import SgSelenium

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	driver = SgSelenium().chrome()
	time.sleep(2)
	
	base_link = "https://www.oakstreethealth.com/locations"

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
	all_links = []
	items = base.find_all(class_="link-list__link link-list__link--hover-bg-green")
	locator_domain = "oakstreethealth.com"

	for item in items:
		link = item["href"]
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		new_items = base.find_all(class_="location-thumb link-thumb")
		for i in new_items:
			all_links.append(i["href"])

	for i, link in enumerate(all_links):
		print("Link %s of %s" %(i+1,len(all_links)))
		print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.h1.text.strip()

		raw_address = base.find(class_="icon-list__title").text.split(",")
		street_address = " ".join(raw_address[:-2]).strip().replace("  "," ")
		city = raw_address[-2].strip()
		state = raw_address[-1].strip()[:3].strip()
		zip_code = raw_address[-1][3:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			raw_types = base.find(class_="location-list__list icon-list type-body").find_all(class_="icon-list__title")
			location_type = ""
			for raw_type in raw_types:
				location_type = location_type + "," + raw_type.text.strip()
			location_type = location_type[1:].strip()
		except:
			location_type = "<MISSING>"
		phone = base.find(class_="icon-list").find_all("a")[-1].text.strip()
		try:
			hours_of_operation = base.find(class_="icon-list__titles").text.replace("\n\n\n"," ").strip()
		except:
			hours_of_operation = "<MISSING>"

		try:
			map_url = base.find(class_="icon-list__item").a["href"]
			req = session.get(map_url, headers = HEADERS)
			map_link = req.url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()

			if len(latitude) > 20:
				driver.get(map_url)
				time.sleep(8)
				map_link = driver.current_url
				at_pos = map_link.rfind("@")
				latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
				longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()

		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"
		if street_address == "2240 East 53rd St Suite B-1":
			latitude = "39.849198"
			longitude = "-86.12594"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
