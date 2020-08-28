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
	
	base_link = "http://www.connectnowonline.com/"

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

	items = base.find(class_="sub-nav level-arrows-on").find_all("a")[1:]
	locator_domain = "connectnowonline.com"

	for item in items:
		link = item["href"]
		if link == "#":
			continue

		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		raw_data = base.find(id="content").find(class_="vc_row wpb_row vc_inner vc_row-fluid")

		location_name = base.h1.text.strip()
		print(link)
		
		raw_address = raw_data.find_all("p")[1].text.replace("\xa0"," ").replace("TX,","TX").split("\n")
		if " PM" in raw_address[0]:
			raw_address = raw_data.find_all("p")[-1].text.replace("\xa0"," ").replace("TX,","TX").split("\n")
		if len(raw_address) == 1:
			raw_address = raw_data.find(class_="address").text.replace("\xa0"," ").split("\n")
			street_address = " ".join(raw_address[:-1]).strip()
			city_line = raw_address[-1].strip().split(",")
		else:
			street_address = " ".join(raw_address[:-2]).strip()
			city_line = raw_address[-2].strip().split(",")
		city = city_line[0].strip()
		state = city_line[-1].strip().split()[0].strip()
		zip_code = city_line[-1].strip().split()[1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		phone = raw_data.find_all("a")[-1].text.strip()

		hours_of_operation = raw_data.find_all("p")[-1].text.replace("\n"," ")
		if "TX" in hours_of_operation:
			hours_of_operation = raw_data.find_all("p")[1].text.replace("\xa0"," ").replace("\n"," ")

		try:
			map_link = base.iframe["src"]
			at_pos = map_link.rfind("!3d")
			latitude = map_link[at_pos+3:map_link.find("!",at_pos+3)].strip()
			longitude = map_link[map_link.find("!2d")+3:at_pos-1].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
