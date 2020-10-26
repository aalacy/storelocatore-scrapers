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
	time.sleep(randint(2,4))
	
	base_link = "https://www.robertwayne.com/pages/locations"

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

	items = base.find_all(class_="Faq__Answer Rte") 
	locator_domain = "robertwayne.com"

	for i, item in enumerate(items):
		print("Element %s of %s" %(i+1,len(items)))
		if "phone" not in item.text.lower():
			continue

		location_name = item.h3.text.strip()
		print(location_name)
		
		raw_address = item.find_all("p")[-2].text.replace(" Northridge"," ,Northridge").split(",")
		street_address = " ".join(raw_address[:-2]).strip()
		city = raw_address[-2].strip()
		if not street_address:
			street_address = " ".join(city.split()[:-1])
			city = city.split()[-1]
		state = raw_address[-1].strip()[:-6].strip()
		zip_code = raw_address[-1][-6:].strip()

		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		phone = item.p.text.split(":")[-1].strip()
		hours_of_operation = item.find_all("p")[1].text.replace("Hours:","").strip()
		if "address" in hours_of_operation.lower():
			hours_of_operation = "<MISSING>"
		
		map_link = item.a['href']
		driver.get(map_link)
		time.sleep(8)

		try:
			map_link = driver.current_url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
