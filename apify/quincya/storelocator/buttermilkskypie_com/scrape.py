from sgselenium import SgSelenium
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

	driver = SgSelenium().chrome()
	time.sleep(2)

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	base_link = "https://www.buttermilkskypie.com/locations/"

	driver.get(base_link)
	time.sleep(8)

	driver.find_element_by_id("filterShowAll").click()
	time.sleep(4)

	base = BeautifulSoup(driver.page_source,"lxml")
	items = base.find(class_="store-locator__store-list").find_all(class_="store-locator__infobox")

	data = []
	
	locator_domain = "buttermilkskypie.com"

	for item in items:
		link_str = str(item.find(class_="infobox__title ssf_image_setting"))
		if "coming_soon" in link_str:
			continue

		link = item.find(class_="infobox__row store-exturl ssflinks")["href"]
		print(link)

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.h3.text.replace("–","-").strip()
		
		street_address = base.find(class_="et-boc").find_all("p")[0].a.text.strip()
		if street_address == "6120 Camp Bowie Blvd Fort Worth, Texas":
			street_address = "6120 Camp Bowie Blvd"
			city = "Fort Worth"
			state = "TX"
			zip_code = "76116"
		elif "\n" in street_address:
			city_line = street_address[street_address.find("\n"):].replace("\xa0"," ").strip().split(",")
			street_address = street_address[:street_address.find("\n")].strip()

		else:
			try:
				city_line = base.find(class_="et-boc").find_all("p")[0].find_all("a")[1].text.split(",")
			except:
				city_line = base.find(class_="et-boc").find_all("p")[1].a.text.split(",")
			city = city_line[0].strip()
			if "suite" in city.lower():
				street_address = street_address + " " + city
				city_line = base.find(class_="et-boc").find_all("p")[0].find_all("a")[2].text.split(",")
				city = city_line[0].strip()
		street_address = street_address.replace("’","'").replace("Â"," ")

		state = city_line[1][:-6].strip()
		zip_code = city_line[1][-6:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = base.find(class_="et-boc").find_all("p")[1].text.replace("Phone:","").strip()
		if "," in phone:
			phone = base.find(class_="et-boc").find_all("p")[2].text.replace("Phone:","").strip()
			hours_of_operation = base.find(class_="et-boc").find_all("p")[3].text.replace("pm","pm ").strip()
		else:
			hours_of_operation = base.find(class_="et-boc").find_all("p")[2].text.replace("pm","pm ").strip()
			next_line = base.find(class_="et-boc").find_all("p")[3].text.replace("pm","pm ").strip()
			if ":" in next_line:
				hours_of_operation = (hours_of_operation + " " + next_line).strip()
		hours_of_operation = hours_of_operation.replace("–","-").replace("Hours","").replace("Â"," ").replace("  "," ").strip()
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
		
		map_link = item.find(class_="infobox__row infobox__cta ssflinks")["href"]
		latitude = map_link.split("(")[-1].split(",")[0]
		longitude = map_link.split("(")[-1].split(",")[1][:-1].strip()

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
