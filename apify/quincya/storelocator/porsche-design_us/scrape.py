from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re

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
	
	base_link = "https://www.porsche-design.us/store-locator/?cl=shops&fnc=search&scallback=radius&sCityZip=&fRadius=&sContinent=&sCountry=US&iShoptype=&sCategory="

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	all_links = []
	data = []

	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(2,4))

	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got main page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.find_all(class_="cell small-12")[1].find_all("div", class_=re.compile("^cell small-12"))[1:]
	for item in items:
		location_name = item.find(class_="h5").text
		if "PORSCHE DESIGN DEALER" in location_name.upper():
			break
		link = item.find(class_="link link--arrow")['href']
		all_links.append(link)

	total_links = len(all_links)
	for i, link in enumerate(all_links):
		print("Link %s of %s" %(i+1,total_links))

		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		locator_domain = "porsche-design.us"

		item = base.find(class_="storefinder__store")
		location_name = item.find('h1').text.strip()
		print(location_name)

		raw_address = str(item.p)[3:].replace("</p>","").replace("\n","").strip().split("<br/>")

		street_address = raw_address[0].strip()
		city_line = raw_address[1].strip()

		try:
			state = re.findall( r"[A-Z]{2} ",city_line)[0].strip()
		except:
			state = "<MISSING>"
		try:
			zip_code = re.findall( r"[0-9]{5}",city_line)[0]
		except:
			zip_code = "<MISSING>"

		city = city_line.replace(zip_code,"").replace(state,"").replace(",","").strip()

		country_code = "US"
		store_number = "<MISSING>"
		phone = item.find(class_="list list--neutral").li.text.replace("Phone:","").strip()

		location_type = "Design Store"

		hours_of_operation = ""
		raw_hours = item.find_all("p")[1].text.replace("\n","").strip()
		hours_of_operation = (re.sub(' +', ' ', raw_hours)).strip()
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		latitude = base.find(class_="window")['data-lat']
		longitude = base.find(class_="window")['data-lng']

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
