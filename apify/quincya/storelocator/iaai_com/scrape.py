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
	
	base_link = "https://www.iaai.com/branchlocations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.find_all(class_="table-row table-row-border")

	for item in items:
		locator_domain = "iaai.com"
		location_name = item.find(class_='heading-7').text.strip()
		print(location_name)

		raw_address = item.find(class_="data-list__value").text.replace("\n","").split(",")

		street_address = raw_address[0].strip()
		city = raw_address[1].strip()
		state = raw_address[2][:raw_address[2].rfind(" ")].strip()
		zip_code = raw_address[2][raw_address[2].rfind(" ")+1:].strip()

		country_code = "US"
		phone = item.find_all(class_="data-list__value")[1].text

		location_type = "<MISSING>"
		hours_of_operation = item.find_all(class_="data-list__value")[4].text

		link = "https://www.iaai.com" + item.a['href']
		# print(link)

		store_number = link.split("/")[-1]

		# Get lat/long
		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			maps = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		try:
			latitude = maps.find(id="BranchModel")['data-latitude']
			longitude = maps.find(id="BranchModel")['data-longitude']
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
