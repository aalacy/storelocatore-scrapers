import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('aspencreekgrill_com')




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
	
	base_link = "https://www.aspencreekgrill.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	driver = get_driver()
	data = []

	items = base.findAll('li', attrs={'class': 'amoteam-tiles__item'})
	for item in items:
		link = item.find('a')['href']

		req = requests.get(link, headers=headers)

		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		locator_domain = "aspencreekgrill.com"
		location_name = base.find('title').text.strip()
		logger.info(location_name)
		section = base.find('div', attrs={'class': 'widget widget_cristiano_contact'})
		raw_data = str(section.p).replace('<p>',"").replace('</p>',"").replace('\n',"").split('<br/>')
		street_address = raw_data[0].strip()
		city = raw_data[1][:raw_data[1].find(',')].strip()
		state = raw_data[1][raw_data[1].find(',')+1:raw_data[1].rfind(' ')].strip()
		zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = str(section.find('a')['href']).replace("tel:","").strip()
		location_type = "<MISSING>"

		driver.get(link)
		time.sleep(2)

		try:
			maps = driver.find_element_by_class_name('col-md-8')
			raw_gps = maps.find_element_by_tag_name('a').get_attribute('href')
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
			longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

		hours = section.find('ul', attrs={'class': 'contact-info'}).get_text(separator=u' ').replace("\n"," ").replace("  "," ").strip()
		hours_of_operation = re.sub(' +', ' ', hours)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
