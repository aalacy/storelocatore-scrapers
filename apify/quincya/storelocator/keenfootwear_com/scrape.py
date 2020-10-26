from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time

from random import randint


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.keenfootwear.com/keen-garages.html"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	req = session.get(base_link, headers = HEADERS)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.find_all(class_="cta-card-center")
	for item in items:
		locator_domain = "keenfootwear.com"
		location_name = "KEEN GARAGES " + item.find('h5').text.strip()
		# print(location_name)

		raw_address = str(item.p)[3:-4].replace("\n","").split("<br/>")[0]

		street_address = raw_address[:raw_address.find(",")]

		city = raw_address[raw_address.find(",")+1:raw_address.rfind(",")].strip()
		state = raw_address[raw_address.rfind(",")+1:raw_address.rfind(" ")].strip()
		zip_code = raw_address[raw_address.rfind(" ")+1:].strip()

		country_code = "US"
		store_number = "<MISSING>"
		phone = str(item.p)[3:-4].replace("\n","").split("<br/>")[1][-15:].strip()

		location_type = "<MISSING>"
		hours_of_operation = ' '.join(str(item.p)[3:-4].replace("\n","").split("<br/>")[2:]).replace('<span class="fw-bold">Hours:</span> ',"")

		link = item.a['href']
		print(link)

		req = session.get(link, headers = HEADERS)

		try:
			maps = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		try:
			map_link = maps.find_all("iframe")[1]['src']
			lat_pos = map_link.rfind("!3d")
			latitude = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
			lng_pos = map_link.find("!2d")
			longitude = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
