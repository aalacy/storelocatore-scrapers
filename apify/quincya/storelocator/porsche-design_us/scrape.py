from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re
from random import randint
from selenium.webdriver.support.ui import Select
from sgselenium import SgSelenium

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	driver = SgSelenium().chrome()
	time.sleep(2)
	
	base_link = "https://www.porsche-design.us/us/en/storelocator/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	driver.get(base_link)
	time.sleep(6)

	state = driver.find_element_by_id("ZipOrLocus")
	state.clear()
	state.send_keys('NY')
	time.sleep(randint(1,2))
	select = Select(driver.find_element_by_id('Distance'))
	select.select_by_value('300')
	time.sleep(randint(1,2))

	search_button = driver.find_element_by_xpath("//*[(@value='Find stores')]")
	driver.execute_script('arguments[0].click();', search_button)
	time.sleep(randint(10,12))

	all_links = []
	data = []

	base = BeautifulSoup(driver.page_source,"lxml")
	items = items = base.find(class_="col-sm-12 col-md-6").find_all(class_="store-search-result-container d-flex")

	for item in items:
		location_name = item.find(class_="h5").text
		link = "https://www.porsche-design.us" + item.find(class_="text-uppercase more-link")['href']
		all_links.append(link)

	total_links = len(all_links)
	for i, link in enumerate(all_links):
		# print("Link %s of %s" %(i+1,total_links))
		req = session.get(link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		locator_domain = "porsche-design.us"
		location_type = "<MISSING>"

		item = base.find(class_="container mt-5")
		location_name = item.find('h1').text.strip()
		print(location_name)

		raw_address = str(item.p)[3:].replace("</p>","").replace("\n","").strip().split("<br/>")

		street_address = raw_address[0].strip()
		if street_address[-1:] == ",":
			street_address = street_address[:-1].strip()
		try:
			city_line = raw_address[1].strip().split(",")
			city = city_line[0].strip()
			state = city_line[-1].strip().split()[0].strip()
			zip_code = city_line[-1].strip().split()[1].strip()
		except:
			street_address = "<MISSING>"
			if location_name == "JFK Airport":
				state = "NY"
				city = "NY"
			else:
				state = "<MISSING>"
				city = "<MISSING>"
			data.append([locator_domain, link, location_name, street_address, city, state, "<MISSING>", country_code, "<MISSING>", "<MISSING>", location_type, "<MISSING>", "<MISSING>", "<MISSING>"])
			continue

		country_code = "US"
		store_number = "<MISSING>"
		raw_phone = item.find_all("p")[1].text.replace("\n","")
		phone = re.findall(r'\+.+ E', raw_phone)[0][:-1].strip()

		hours_of_operation = ""
		raw_hours = item.find_all("p")[3].text.replace("\n","").strip()
		hours_of_operation = (re.sub(' +', ' ', raw_hours)).strip()
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		latitude = "<MISSING>"
		longitude = "<MISSING>"
		all_scripts = base.find_all('script')
		for script in all_scripts:
			if "lng" in str(script):
				script = str(script)
				coords = re.findall(r'\[-.+,.+\]},', script)[0]
				latitude = coords.split(",")[1][:-2]
				longitude = coords.split(",")[0][1:]
				break

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
