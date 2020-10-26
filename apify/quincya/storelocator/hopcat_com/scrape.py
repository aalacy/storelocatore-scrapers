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
	
	base_link = "https://hopcat.com/"

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

	main_links = []
	main_items = base.find(class_="item-list").find_all('a') 
	for main_item in main_items:
		if "HopCat" in main_item.text:
			main_link = "https://hopcat.com" + main_item['href']
			main_links.append(main_link)

	data = []
	for final_link in main_links:
		final_req = session.get(final_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(final_req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		locator_domain = "hopcat.com"

		location_name = item.find('option', selected=True).text
		print(location_name)

		raw_data = item.find(id="utility_nav").find(class_="view-content").find_all('li')
		raw_address = raw_data[0].text.replace("Ave. ", "Ave, ").replace("Michigan,","MI").replace("ST. ", "ST, ").replace("St. ", "ST, ")\
		.replace(" Corner of P & Canopy","").replace("Rapids MI", "Rapids, MI").replace("KY, ","KY ").replace("MI, ","MI ").replace("Mi, ","MI ").split(",")
		street_address = raw_address[0].strip()

		try:
			city = raw_address[1].strip()
			try:
				state = raw_address[2][:-6].strip()
				zip_code = raw_address[2][-6:].strip()
				if not zip_code.isnumeric():
					state = raw_address[2][-3:].strip()
					zip_code = "<MISSING>"
			except:
				state = city[-3:].strip()
				city = city[:-3].strip()
				zip_code = "<MISSING>"
		except:
			state = "<MISSING>"
			city = "<MISSING>"
			zip_code = "<MISSING>"

		country_code = "US"
		store_number = "<MISSING>"
		
		location_type = "<MISSING>"

		try:
			phone =  raw_data[2].text.strip()
		except:
			phone = "<MISSING>"

		hours_of_operation = raw_data[1].text.strip()

		map_link = raw_data[-1].a['href']
		try:
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
