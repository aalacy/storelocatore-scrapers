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

	base_link = "https://stonefiregrill.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')
	
	section = base.find('ul', attrs={'class': 'location_grid clearfix'})
	items = section.findAll('li')
	
	driver = get_driver()
	data = []
	for item in items:

		link = item.find('a')['href']

		req = requests.get(link, headers=headers)
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')

		locator_domain = "stonefiregrill.com"
		content = base.find('div', attrs={'class': 'row'})
		location_name = content.find('h1').text.strip()
		print (location_name)
		
		raw_data = str(base.find('span', attrs={'itemprop': 'address'})).replace('<p>',"").replace('</p>',"").replace('\n',"").replace(',',"").split('<br/>')
		street_address = content.find('span', attrs={'class': 'address'}).text.strip()
		raw_line = base.find('span', attrs={'class': 'city'}).text.strip()
		city = raw_line[:raw_line.rfind(',')].strip()
		state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		if state == "":
			state = "<MISSING>"
		country_code = "US"
		store_number = "<MISSING>"
		phone = base.find('span', attrs={'class': 'phone strong'}).text.strip()
		location_type = "<MISSING>"

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

		hours_of_operation = content.find('table', attrs={'class': 'wpsl-opening-hours'}).get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data
	driver.close()

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
