from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
import sgzip

from random import randint
from sgselenium import SgSelenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('poolcorp_com')


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	base_link = "https://www.poolcorp.com/map_api/map.php"

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)

	base = BeautifulSoup(req.text,"lxml")
	js = base.text.split("var LocsAB =")[-1][:-1]
	stores = json.loads(js)

	base_link = "https://www.poolcorp.com/sales-centers/index.html?z="

	driver = SgSelenium().chrome()
	time.sleep(2)

	all_links = []
	found_poi = []

	zips = sgzip.for_radius(175)
	for zip_code in zips:
		logger.info(zip_code)
		link = base_link+zip_code
		driver.get(link)
		time.sleep(randint(2,4))

		try:
			element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
				(By.CSS_SELECTOR, ".container.mt-3.mb-5")))
			time.sleep(randint(3,5))
		except:
			continue

		base = BeautifulSoup(driver.page_source,"lxml")
		items = base.find_all(class_="row dealer_row")

		for item in items:
			name = item.h3.text.strip()
			if name not in found_poi:
				if "colombia" in name.lower() or "puerto rico"  in name.lower():
					continue
				# logger.info(name)
				all_links.append([name,item,link])
				found_poi.append(name)

	# can_zips = ["T9S", "A0C", "L7J", "Y0B", "V3G", "X0E", "C0A", "R0K", "B1Y", "J0Y",
	# 			"E8L", "X0B", "S2V"]

	# for can_zip in can_zips:
	# 	link = base_link+can_zip
	# 	driver.get(link)
	# 	time.sleep(randint(2,4))
	# 	logger.info(can_zip)

	# 	try:
	# 		element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
	# 			(By.CSS_SELECTOR, ".container.mt-3.mb-5")))
	# 		time.sleep(randint(3,5))
	# 	except:
	# 		continue

	# 	base = BeautifulSoup(driver.page_source,"lxml")
	# 	items = base.find_all(class_="row dealer_row")

	# 	for item in items:
	# 		name = item.h3.text.strip()
	# 		if name not in found_poi:
	# 			if "colombia" in name.lower() or "puerto rico"  in name.lower():
	# 				continue
	# 			logger.info(name)
	# 			all_links.append([name,item,link])
	# 			found_poi.append(name)

	data = []
	total_links = len(all_links)
	for i, raw_link in enumerate(all_links):
		location_name = raw_link[0]
		item = raw_link[1]
		link = raw_link[2]

		locator_domain = "poolcorp.com"

		raw_address = str(item.p)[3:str(item.p).find("<a")-5].split("<br/>")
		street_address = raw_address[0].replace("amp;","").strip()

		comma_pos = raw_address[1].find(",")
		city = raw_address[1][:comma_pos].strip()
		state =  raw_address[1][comma_pos+2:raw_address[1].find(" ", comma_pos+3)].strip()
		if "-" in state:
			state = location_name.split(",")[1].split("-")[0].strip()

		if state == "QLD" or state == "NSW":
			continue
		zip_code = raw_address[1][raw_address[1].find(" ", comma_pos+3):].strip()
		if " " in zip_code:
			country_code = "CA"
		else:
			country_code = "US"

		try:
			store_number = location_name.split()[-1]
		except:
			store_number = "<MISSING>"
		try:
			phone = item.a['href']
			if "tel:" in phone:
				phone = phone.replace("tel:","").replace("(","").replace(") ","-")
			if not phone[-3:].isnumeric():
				phone = "<MISSING>"
		except:
			phone = "<MISSING>"

		logo = item.img['src'].split("/")[-1]
		if "scp" in logo:
			location_type = "SCP Distributors LLC"
		elif "spp" in logo:
			location_type = "Superior Pool Products"
		elif "horizon" in logo:
			location_type = "Horizon Distributors Inc"
		elif "npt" in logo:
			location_type = "NPT"
		elif "jetline" in logo:
			location_type = "Jet Line"
		else:
			location_type = logo

		hours_of_operation = "<MISSING>"

		latitude = "<MISSING>"
		longitude = "<MISSING>"

		if store_number != "<MISSING>":
			for store in stores:
				store_id = store["title"].split("-")[0].strip()
				if store_id == store_number:
					latitude = store["lat"]
					longitude = store["lon"]
					break

		location_name = "POOLCORP - " + location_name.split(",")[0].strip()

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	
	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
