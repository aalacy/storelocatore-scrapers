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
	
	base_link = "https://www.gradysbbq.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.findAll('p', attrs={'class': 'locationsList'})

	driver = get_driver()
	data = []
	for item in items:
		locator_domain = "gradysbbq.com"
		raw_link = item.a['href']
		link = "https://www.gradysbbq.com/locations/" + raw_link[raw_link.rfind("/")+1:]
		location_name = item.find('a').text.strip()
		print (location_name)
		raw_address = item.text.strip()
		street_address = raw_address[raw_address.find("   ")+1:raw_address.rfind("   ")].replace("\n","").strip()
		if "," in street_address:					
			city = street_address[street_address.rfind(',')-8:street_address.rfind(',')].strip()
			state = street_address[street_address.rfind(',')+1:].strip()
			street_address = street_address[:street_address.find(',')]
		else:
			city = "<MISSING>"
			state = "<MISSING>"
		zip_code = "<MISSING>"
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = item.findAll('a')[1].text.strip()
		except:
			phone = "<MISSING>"
		location_type = "<MISSING>"

		req = requests.get(link, headers=headers)

		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')

		driver.get(link)
		time.sleep(2)

		try:
			maps = driver.find_element_by_class_name('fullwidth')
			raw_gps = maps.find_element_by_tag_name('a').get_attribute('href')
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

		hours = base.find('div', attrs={'class': 'col'}).get_text(separator=u' ').replace("\n"," ").replace("  "," ").strip()
		hours_of_operation = re.sub(' +', ' ', hours)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
