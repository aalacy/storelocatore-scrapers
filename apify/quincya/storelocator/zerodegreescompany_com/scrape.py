from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sgselenium import SgSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
	
	base_link = "https://www.zerodegreescompany.com/locations"

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

	items = base.find(id="rda7cinlineContent-gridContainer").find_all('div', {'class': re.compile(r'style-.+inlineContent')})
	locator_domain = "zerodegreescompany.com"

	data = []
	found_poi = []

	for item in items:
		location_name = item.h6.text
		if "coming" in location_name.lower():
			continue
		try:
			raw_address = item.a.span.text.replace("Las Vegas ","Las Vegas, ").replace(location_name,"|").split("|")
		except:
			continue
		street_address = raw_address[0].strip()
		if street_address in found_poi:
			continue
		print(location_name)
		found_poi.append(street_address)
		city = location_name.split(",")[0].strip()
		state = location_name.split(",")[1].strip()
		if "(" in state:
			state = state.split("(")[0].strip()
		try:
			zip_code = raw_address[1].strip()
		except:
			raw_address = item.a.span.text.replace("Las Vegas ","Las Vegas, ").split(",")
			try:
				street_address = (raw_address[-4] + " " + raw_address[-3]).strip()
			except:
				street_address = raw_address[-3].strip()
			street_address = street_address.replace("  "," ")
			zip_code = raw_address[-1].strip().split()[-1]
		if street_address[-1:] == ",":
			street_address = street_address[:-1]
		country_code = "US"
		location_name = "Zero Degrees - " + location_name
		store_number = "<MISSING>"
		location_type = ""
		raw_types = item.find_all('div', attrs={'data-state': "desktop shouldUseFlex center"})
		for loc_type in raw_types:
			location_type = location_type + "," + loc_type.text
		location_type = location_type[1:].strip()
		try:
			phone = item.find('a', attrs={'data-type': "phone"})["data-content"]
		except:
			phone = item.find_all("p")[-1].text

		try:
			map_url = item.a['href']
			req = session.get(map_url, headers = HEADERS)
			map_link = req.url
			at_pos = map_link.rfind("3d")
			latitude = map_link[at_pos+2:map_link.rfind("!", at_pos)].strip()
			longitude = map_link[map_link.rfind("d")+1:].strip()
			if "?" in longitude:
				longitude = longitude.split("?")[0]
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"
		if street_address == "1807 N Collins St":
			latitude = "32.763059"
			longitude = "-97.096259"
		if street_address == "1700 W Sand Lake Rd Suite D123B":
			latitude = "28.4486408"
			longitude = "-81.403508"
		if street_address == "11401 Broadway St #101":
			latitude = "29.556159"
			longitude = "-95.3969614"

		link = item.find_all('a', attrs={'data-type': "external"})[1]["href"].replace("s/order","")
		driver.get(link)
		time.sleep(randint(1,2))
		hours_of_operation = "<MISSING>"

		if "yelp" in link:
			try:
				hours = base.find(class_="lemon--tbody__373c0__2T6Pl").text.replace("pm","pm ").replace("PM","PM ").replace("Closed","Closed ").strip()
				hours_of_operation = (re.sub(' +', ' ', hours)).strip()
			except:
				pass
		else:
			try:
				element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
					(By.CSS_SELECTOR, ".w-cell.user-content.row")))
				time.sleep(randint(8,10))
				try:
					raw_hours = driver.find_element_by_xpath("//div[(@data-block-purpose='location-hours@^1.0.0')]").find_elements_by_tag_name("p")
				except:
					raw_hours = ""
				if not raw_hours:
					time.sleep(randint(20,30))
					raw_hours = driver.find_element_by_xpath("//div[(@data-block-purpose='location-hours@^1.0.0')]").find_elements_by_tag_name("p")
				for raw_hour in raw_hours:
					raw_hour = raw_hour.text.strip()
					try:
						if "day " in raw_hour.lower() or "am" in raw_hour.lower() or " pm" in raw_hour.lower():
							hours = raw_hour.replace("\n"," ").strip()
							hours_of_operation = (re.sub(' +', ' ', hours)).strip()
							break
					except:
						continue
			except:
				hours_of_operation = "<MISSING>"

			if hours_of_operation == "<MISSING>":
				base = BeautifulSoup(driver.page_source,"lxml")

				fin_script = ""
				all_scripts = base.find_all('script')
				for script in all_scripts:
					if "latitude" in str(script):
						fin_script = script.text.replace('\n', '').strip()
						break

				if fin_script:
					try:
						hours_pos = fin_script.find("location-hours@")
						raw_hours = fin_script[hours_pos:fin_script.find("]}}",hours_pos)]
						hours = re.findall(r'insert.+}',raw_hours)[0][8:-2].replace("\\n"," ")
						hours_of_operation = (re.sub(' +', ' ', hours)).strip()
					except:
						pass
		hours_of_operation = hours_of_operation.replace('"','').replace("*Kitchen closes 30 minutes early","").strip()
		if hours_of_operation == "11:00AM-10:00PM":
			hours_of_operation = "Mon-Sun 11:00AM-10:00PM"
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"
		if "ubereats" in link or "postmates" in link or "zdkaty." in link:
			link = base_link
		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
