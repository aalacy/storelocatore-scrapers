import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #return webdriver.Chrome(executable_path='driver/chromedriver', chrome_options=options)
    return webdriver.Chrome('chromedriver', chrome_options=options)


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.pacificpowerbatteries.com"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	driver = get_driver()
	driver.get(base_link)
	time.sleep(2)

	section = driver.find_elements_by_css_selector('.dropdown-content')[1]
	links = section.find_elements_by_tag_name('a')
	items = []
	for i in links:
		items.append(i.get_attribute('href'))

	data = []
	for link in items:
		req = requests.get(link, headers=headers)

		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')

		locator_domain = "pacificpowerbatteries.com"
		content = base.find('div', attrs={'class': 'container well'})
		city = content.find('h1').text.strip()
		location_name = base.find('title').text.strip() + " - " + city
		print (location_name)
		raw_line = content.find('a').text.strip()
		street_address = raw_line[:raw_line.find(city)].strip()
		state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
		if "Mountlake Terrace" in state:
			state = "WA"
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = re.findall("[[(\d)]{5}.+[\d]{3}.+[\d]{4}", content.text)[0]
		if len(phone) > 20:
			phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", content.text)[0]
		location_type = "<MISSING>"
		try:
			map_link =content.find('a')['href']
			driver.get(map_link)
			time.sleep(2)
			raw_gps = driver.current_url
			start_point = raw_gps.find("@") + 1
			latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
			long_start = raw_gps.find(',',start_point)+1
			longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"
			
		hours_of_operation = content.findAll('div', attrs={'class': 'media-body'})[1].get_text(separator=u' ').replace("\n"," ").replace("\xa0"," ").replace("  "," ").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)
		hours_of_operation = hours_of_operation[:hours_of_operation.rfind('pm')+2].strip()

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
