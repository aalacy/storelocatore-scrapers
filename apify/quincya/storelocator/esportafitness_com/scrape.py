from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def get_driver():
	options = Options() 
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('--window-size=1920,1080')
	return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.esportafitness.com/Pages/FindClub.aspx"

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

	states = base.find(id="ctl00_MainContent_FindAClub1_cboSelState").find_all("option")[1:]

	driver = get_driver()
	time.sleep(2)

	final_links = []
	for raw_state in states:
		state = raw_state['value']
		main_link = "https://www.esportafitness.com/Pages/findclubresultszip.aspx?state=" + state
		print(main_link)

		driver.get(main_link)
		time.sleep(randint(2,4))

		try:
			element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
				(By.CSS_SELECTOR, ".TextDataColumn")))
			time.sleep(randint(2,4))
		except:
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		count = 0
		while True and count < 5:
			base = BeautifulSoup(driver.page_source,"lxml")
			main_items = base.find_all(class_='TextDataColumn')
			for main_item in main_items:
				main_link = "https://www.esportafitness.com/Pages/" + main_item.a['href']
				final_links.append(main_link)
			try:
				driver.find_element_by_id("ctl00_MainContent_lnkNextTop").click()
				time.sleep(randint(4,6))
				count += 1
			except:
				break

	data = []
	total_links = len(final_links)
	for i, final_link in enumerate(final_links):
		print("Link %s of %s" %(i+1,total_links))
		print(final_link)
		final_req = session.get(final_link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(final_req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		locator_domain = "esportafitness.com"

		location_name = item.h1.text.strip()
		# print(location_name)

		try:
			street_address = item.find(id="ctl00_MainContent_lblClubAddress").text
		except:
			continue
		city = item.find(id="ctl00_MainContent_lblClubCity").text
		state = item.find(id="ctl00_MainContent_lblClubState").text
		zip_code = item.find(id="ctl00_MainContent_lblZipCode").text
		country_code = "US"
		store_number = re.findall('clubid=[0-9]+',final_link)[0].split("=")[1].strip()
		location_type = "<MISSING>"
		phone = item.find(id="ctl00_MainContent_lblClubPhone").text
		if "Reg" in phone:
			phone = phone[:phone.find("Reg")].strip()
		latitude = "<MISSING>"
		longitude = "<MISSING>"

		hours_of_operation = item.find(id="divClubHourPanel").text.replace("pm","pm ").replace("CLUB HOURS","").strip()

		data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
