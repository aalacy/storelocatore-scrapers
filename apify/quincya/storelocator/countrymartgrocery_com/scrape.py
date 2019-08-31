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
	
	base_link = "http://www.countrymartgrocery.com/stores.php?view=all"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	section = base.findAll('table')[-2]
	items = section.findAll('td')

	driver = get_driver()
	data = []

	for item in items:
		
		locator_domain = "countrymartgrocery.com"
		try:
			link = "http://www.countrymartgrocery.com/" + item.find('a')['href']
			zip_code = item.find('a').text
			zip_code = zip_code[zip_code.rfind(",")+1:zip_code.rfind("|")-1].strip()
		except:
			continue
		try:
			location_type = item.find('span').text.strip()
			if location_type == "":
				location_type = "<MISSING>"
		except:
			location_type = "<MISSING>"

		req = requests.get(link, headers=headers)

		try:
			new_base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')
		
		table = new_base.find('table')

		raw_data = new_base.findAll('td')[1]
		raw_data = raw_data.findAll('div')[1].text.strip()
		
		street_address = raw_data[:raw_data.find(',')].strip()
		city = raw_data[raw_data.find(',')+1:raw_data.rfind(',')].strip()
		state = raw_data[raw_data.rfind(',')+1:].strip()
		location_name = new_base.find('u').text.strip() + " " + city.upper()
		print (location_name)
		country_code = "US"
		store_number = link[link.rfind("=")+1:]
		
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", str(item))[0]
		except:
			phone = "<MISSING>"

		driver.get(link)
		time.sleep(2)

		try:
			maps = driver.find_element_by_class_name('gm-style')
			raw_gps = maps.find_element_by_tag_name('a').get_attribute('href')
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

		hours = new_base.find('td', attrs={'class': 'store_detail_box'}).get_text(separator=u' ').replace("\n"," ").replace("\x96","").replace("  "," ").strip()
		hours_of_operation = re.sub(' +', ' ', hours)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
