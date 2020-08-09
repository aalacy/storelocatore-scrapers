from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.picturehouses.com/cinema?search="

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

	items = base.find(class_="cinemaPage_list cinema_desktop_view").find_all(class_="hovereffect")
	locator_domain = "picturehouses.com"

	for item in items:

		link = item.a["href"] + "/information"
		print(link)
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		
		raw_address = str(base.find(class_="cinemaAdrass"))
		raw_address = raw_address[raw_address.find("</i>")+4:].replace("</div>","").split("<br/>")

		location_name = raw_address[0]
		street_address = raw_address[1].strip()
		city = raw_address[-2].strip()
		if "Street" in city:
			street_address = raw_address[-2].strip()
			city = raw_address[1].strip()
		if "," in city:
			street_address = street_address + " " + city.split(",")[0]
			city = city.split(",")[1].strip()

		state = "<MISSING>"
		zip_code = raw_address[-1].strip()
		country_code = "GB"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = "<MISSING>"
		try:
			hours_of_operation = base.find(id="opening-times").text.replace("Opening Times","").replace("each day.","").replace("every day and close around","-").strip()
		except:
			hours_of_operation = "<MISSING>"
		if "Downstairs" in hours_of_operation:
			hours_of_operation = hours_of_operation[:hours_of_operation.find("Downstairs")].strip()
		if "Due" in hours_of_operation:
			hours_of_operation = hours_of_operation[:hours_of_operation.find("Due")].strip()
		if "Mon-Sat" in hours_of_operation:
			hours_of_operation = hours_of_operation[hours_of_operation.find("Mon-Sat"):].strip()
		if "before" in hours_of_operation:
			hours_of_operation = "<MISSING>"
		if "at " in hours_of_operation:
			hours_of_operation = hours_of_operation[hours_of_operation.find("at")+2:].strip()
		if hours_of_operation[-1:] == ".":
			hours_of_operation = hours_of_operation[:-1]
		try:
			raw_gps = base.find(class_="location_map").iframe['src']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
