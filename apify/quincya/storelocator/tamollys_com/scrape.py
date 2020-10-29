import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tamollys_com')




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

	base_link = "http://tamollys.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	section = base.find('div', attrs={'class': 'b2b-location-items'})
	items = section.findAll('li')
	driver = get_driver()
	data = []
	for item in items:
		locator_domain = "tamollys_com"		
		location_name = item.find('h2').text.strip()
		logger.info(location_name)
		
		raw_data = str(item.find('p')).replace('<p>',"").replace('</p>',"").replace('\n',"").strip().split('<br/>')
		street_address = raw_data[0].strip()
		raw_line = raw_data[1].strip()
		city = raw_line[:raw_line.rfind(',')].strip()
		state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[(\d)]{5}.+[\d]{3}.+[\d]{4}", item.text)[0]
		except:
			phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", item.text)[0]
		location_type = "<MISSING>"

		hours_of_operation = base.find('p', attrs={'class': 'b2b-location-detail-info'}).get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)
		hours_of_operation = hours_of_operation[hours_of_operation.find('Hours')+5:].strip()

		try:
			link = item.find('a')['href']
			driver.get(link)
			time.sleep(4)
			raw_gps = driver.current_url
			start_point = raw_gps.find("@") + 1
			latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
			long_start = raw_gps.find(',',start_point)+1
			longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
