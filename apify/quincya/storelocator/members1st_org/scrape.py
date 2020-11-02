from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('members1st_org')



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
	time.sleep(2)
	
	base_link = "https://www.members1st.org/atm-and-locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		logger.info("Got today page")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.find(class_="row justify-content-between").find_all("li")
	locator_domain = "members1st.org"

	data = []
	for item in items:
		link = "https://www.members1st.org" + item.a["href"]
		logger.info(link)
		driver.get(link)
		time.sleep(randint(2,4))
		base = BeautifulSoup(driver.page_source,"lxml")

		location_name = base.h1.text.strip()
		street_address = base.find('span', attrs={'itemprop': "streetAddress"}).text.strip()
		city = base.find('span', attrs={'itemprop': "addressLocality"}).text.split(",")[0].strip()
		state = base.find('span', attrs={'itemprop': "addressLocality"}).text.split(",")[1].strip()
		zip_code = base.find('span', attrs={'itemprop': "postalCode"}).text.strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = base.find(class_="services-table").text.strip().replace("\n",",")
		phone = base.find('span', attrs={'itemprop': "telephone"}).text.replace("Phone:","").strip()
		hours_of_operation = base.find(class_="lobby-hours").text.replace("Lobby Hours","").strip().replace("\n", " ")
		hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
		map_frame = driver.find_element_by_class_name("b_map_img")
		driver.switch_to.frame(map_frame)
		time.sleep(randint(1,2))
		try:
			raw_gps = driver.find_element_by_tag_name("a").get_attribute("href")
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
