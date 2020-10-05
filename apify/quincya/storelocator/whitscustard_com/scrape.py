from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
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
	
	base_link = "https://whitscustard.com/findyourwhits"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")
	
	main_links = []
	items = base.find(class_="sqs-gallery").find_all("a")
	for i in items:
		main_links.append("https://whitscustard.com" + i["href"])

	final_links = []
	for main_link in main_links:
		req = session.get(main_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		items = base.find_all(class_="summary-thumbnail-outer-container")
		for i in items:
			if "Opening%2Bsoon" not in str(i):
				final_links.append("https://whitscustard.com" + i.a["href"])


	data = []
	locator_domain = "whitscustard.com"

	for link in final_links:
		print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		location_name = base.find(class_="entry-title").text.encode("ascii", "replace").decode().replace("?","-").strip()
		
		raw_address = str(base.address).replace("<address>","").replace("</address>","").replace("SUITE 101,","SUITE 101<br/>").replace("HWY HENDER","HWY<br/>HENDER").replace("\nSUITE"," SUITE").replace("RD.\n","RD. ").replace("WEST, \n","WEST, ").split("<br/>")
		street_address = raw_address[0].strip()
		if street_address == "None":
			raw_address = base.h3.text.replace("NUE ZAN","NUE<br/>ZAN").split("<br/>")
			street_address = raw_address[0].strip()
		if "\n" in street_address:
			raw_address = base.address.text.strip().split("\n")
			street_address = raw_address[0].strip()
		city_line = raw_address[1].strip().split(",")
		if len(city_line) == 2:
			city = city_line[0]
			state = city_line[1].split()[0]
			zip_code = city_line[1].split()[1]
		elif len(city_line) == 3:
			city = city_line[0]
			state = city_line[1].strip()
			zip_code = city_line[2].strip()
		elif len(city_line) == 1:
			city_line = city_line[0].split()
			city = city_line[0]
			state = city_line[1]
			zip_code = city_line[2]

		else:
			raise

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		try:
			phone = base.find('a', {'href': re.compile(r'tel')})["href"].replace("tel:","").strip()
		except:
			phone = "<MISSING>"
		if not phone:
			phone = "<MISSING>"

		hours_of_operation = base.find_all(class_="col sqs-col-3 span-3")[-1].text.replace("Hours","").replace("PM","PM ").replace("Drive-thru only","").replace("closed","closed ").strip()
		hours_of_operation = hours_of_operation.encode("ascii", "replace").decode().replace("?","-")

		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		map_link = ""
		maps = base.find_all("a")
		for i in maps:
			if "Directions" in i.text:
				map_link = i["href"].strip()
				break
		if map_link:
			req = session.get(map_link, headers = HEADERS)
			maps = BeautifulSoup(req.text,"lxml")
			try:
				raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
				latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
				longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
		else:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		if len(latitude) > 20:
			old_lat = latitude
			latitude = old_lat.split("=")[-1].split(",")[0]
			longitude = old_lat.split("=")[-1].split(",")[1]
		if "11362 SAN JOSE BLVD" in street_address.upper():
			latitude = "30.1677275"
			longitude = "-81.6349426"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
