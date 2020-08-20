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
	
	base_link = "https://www.intownsuites.com/extended-stay-locations/"

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
	found_poi = []
	items = base.find(id="locationsList").find_all("li")
	locator_domain = "intownsuites.com"

	for item in items:
		link = item.a["href"]
		if link[:2] == "//":
			link = "https:" + link
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		try:
			new_items = base.find_all(class_="col-sm-5")[:-1]
			for new_item in new_items:
				link = new_item.a["href"]
				if link not in all_links:
					all_links.append(link)
		except:
			if link not in all_links:
				all_links.append(link)

	for link in all_links:
		print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		all_scripts = base.find_all('script', attrs={'type': "application/ld+json"})
		for script in all_scripts:
			if "latitude" in str(script):
				script = script.text.replace('\n', '').strip()
				break

		store = json.loads(script)
		location_name = store['name'].replace("&#8211;","-").replace("–","-")
		street_address = store['address']['streetAddress']
		city = store['address']['addressLocality']
		state = store['address']['addressRegion']
		zip_code = store['address']['postalCode']
		country_code = "US"
		store_number = "<MISSING>"
		location_type = str(base.find(class_="property_features").ul).replace("</li><li>",",").replace("</li> </ul>","").replace("<ul>\n<li>","")
		phone = store['telephone'].replace("(Spanish or English)","").strip()
		try:
			hours_of_operation = base.find(class_="css_table_cell office_hours").find_all("p")[-1].text.replace("\n"," ").strip()
			if "Please" in hours_of_operation:
				hours_of_operation = hours_of_operation[:hours_of_operation.find("Please")].strip()
		except:
			hours_of_operation = "<MISSING>"

		latitude = store['geo']['latitude']
		longitude = store['geo']['longitude']

		if location_name not in found_poi:
			found_poi.append(location_name)
			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
