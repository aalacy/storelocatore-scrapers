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
	
	base_link = "https://www.plazaazteca.com/locations-hours"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	headings = base.findAll('h3', attrs={'class': 'header-4'})
	details = base.findAll('div', attrs={'class': 'row location'})
	driver = get_driver()
	data = []
	for index in range(0,len(headings)):

		locator_domain = "plazaazteca.com"
		location_name = headings[index].text.strip()
		if "*" in location_name:
			location_name = location_name[:location_name.find("*")].strip()
		location_type = "<MISSING>"	
		print (location_name)

		raw_data = str(details[index].find('div', attrs={'class': 'col-xs-6 address-info'}).p).replace('<p>',"").replace('</p>',"").replace('\n',"").split('<br/>')
		street_address = raw_data[0].replace('Â','').strip()
		raw_line = raw_data[1].strip()
		city = raw_line[:raw_line.rfind(',')].strip()
		state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = raw_data[2].strip()

		try:
			link = details[index].find('a')['href']
			driver.get(link)
			time.sleep(3)
			raw_gps = driver.current_url
			start_point = raw_gps.find("@") + 1
			latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
			long_start = raw_gps.find(',',start_point)+1
			longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
			try:
				int(latitude[4:8])
			except:
				time.sleep(2)
				raw_gps = driver.current_url
				start_point = raw_gps.find("@") + 1
				latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
				long_start = raw_gps.find(',',start_point)+1
				longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = details[index].find('div', attrs={'class': 'col-xs-6 hours-info'}).get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)
		if hours_of_operation == "":
			hours_of_operation = "<MISSING>"

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
