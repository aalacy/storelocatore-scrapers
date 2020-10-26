import csv
import time
from random import randint
import re
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
	time.sleep(2)

	map_driver = SgSelenium().chrome()
	time.sleep(2)
	
	base_link = "https://www.helegas.com/"

	driver.get(base_link)
	time.sleep(randint(4,6))
	driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
	time.sleep(1)
	driver.find_element_by_class_name("i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c").click()
	time.sleep(1)
	driver.find_element_by_class_name("HzV7m-pbTTYe-KoToPc-ornU0b").click()
	time.sleep(1)
	items = driver.find_elements_by_class_name("suEOdc")[3:-1]

	data = []
	locator_domain = "helegas.com"

	for item in items:
		print(item.text)
		item.click()
		time.sleep(1)
		location_name = item.text.strip()
		raw_address = driver.find_element_by_class_name("fO2voc-jRmmHf-MZArnb-Q7Zjwb").text.split(",")
		street_address = raw_address[0].strip()
		city = raw_address[1].strip()
		state = raw_address[-1].split()[0].strip()
		zip_code = raw_address[-1].split()[1].strip()
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"
		try:
			phone = re.findall("\+1 [(\d)]{3}-[\d]{3}-[\d]{4}", driver.find_element_by_class_name("qqvbed-bN97Pc").text)[0]
		except:
			phone = "<MISSING>"
		hours_of_operation = "<MISSING>"

		map_link = driver.find_element_by_class_name("fO2voc-jRmmHf-LJTIlf-OzwZjf-hSRGPd").find_element_by_tag_name("a").get_attribute("href")
		map_driver.get(map_link)
		time.sleep(8)

		try:
			map_link = map_driver.current_url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
		driver.find_element_by_css_selector(".HzV7m-tJHJj-LgbsSe-Bz112c.qqvbed-a4fUwd-LgbsSe-Bz112c").click()
		time.sleep(1)
	map_driver.close()
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
