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
	
	base_link = "https://espressoroyalecoffee.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	content = base.findAll('div', attrs={'class': 'ms-maincontent'})[1]
	locations = content.findAll('div')

	driver = get_driver()

	data = []
	for location in locations:
		try:
			loc_link = location.a['href']
		except:
			continue

		req = requests.get(loc_link, headers=headers)

		try:
			loc_base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')
		
		location_names = loc_base.findAll('div', attrs={'class': 'loc_link'})

		for loc in location_names:
			link = loc.a['href']
			print ('Getting link: ' + link)
			req = requests.get(link, headers=headers)

			try:
				new_base = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				print ('[!] Error Occured. ')
				print ('[?] Check whether system is Online.')

			locator_domain = "espressoroyalecoffee.com"
			heading = new_base.findAll('div', attrs={'class': 'row'})[1]
			location_name = heading.find('h3').text
			try:
				street_address = new_base.find('div', attrs={'class': 'loc_street'}).text
			except:
				continue
			raw_data = new_base.find('div', attrs={'class': 'loc_city'}).text
			city = raw_data[:raw_data.find(',')].strip()
			state = raw_data[raw_data.find(',')+1:raw_data.rfind(' ')].strip()
			zip_code = raw_data[raw_data.rfind(' ')+1:].strip()
			country_code = "US"
			store_number = "<MISSING>"
			raw_phone = new_base.find('div', attrs={'class': 'loc_phone'}).text
			phone = re.findall("[[\d]{3}.[\d]{3}.[\d]{4}", raw_phone)[0]
			location_type = "<MISSING>"
			latitude = "<MISSING>"
			longitude = "<MISSING>"
			hours_of_operation = new_base.find('div', attrs={'class': 'loc_description'}).get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
			hours_of_operation = re.sub(' +', ' ', hours_of_operation)

			driver.get(link)
			time.sleep(2)
			try:
				maps = driver.find_element_by_class_name('gm-style')
				raw_gps = maps.find_element_by_tag_name('a').get_attribute('href')

				latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
				longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
			except:
				try:
					time.sleep(2)
					maps = driver.find_element_by_class_name('gm-style')
					raw_gps = maps.find_element_by_tag_name('a').get_attribute('href')

					latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
					longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
				except:
					latitude = "<INACCESSIBLE>"
					longitude = "<INACCESSIBLE>"

			data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
			print ('Got page details')

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()