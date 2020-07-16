from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
	options = Options() 
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('--window-size=1920,1080')
	return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	driver = get_driver()
	time.sleep(2)

	base_link = "https://crazymocha.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	session = SgRequests()

	req = session.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.findAll('p', attrs={'style': 'white-space:pre-wrap;'})[1:]

	data = []
	for item in items:
		locator_domain = "crazymocha.com"
		location_name = item.find('strong').text.strip()
		print (location_name)
		raw_data = str(item).replace('<p>',"").replace('</p>',"").replace('\n',"").replace('\xa0',"").split('<br/>')
		street_address = raw_data[1][raw_data[1].rfind(">")+1:raw_data[1].find(",")].strip()
		if street_address:
			city = raw_data[1][raw_data[1].find(',')+1:raw_data[1].rfind(',')].strip()
			state = raw_data[1][raw_data[1].rfind(',')+1:raw_data[1].rfind(',')+4].strip()
			zip_code = raw_data[1][raw_data[1].rfind(',')+4:raw_data[1].rfind(',')+10].strip()
		else:
			street_address = raw_data[0][raw_data[0].rfind(">")+1:raw_data[0].find(",")].strip()
			city = raw_data[0][raw_data[0].find(',')+1:raw_data[0].rfind(',')].strip()
			state = raw_data[0][raw_data[0].rfind(',')+1:raw_data[0].rfind(',')+4].strip()
			zip_code = raw_data[0][raw_data[0].rfind(',')+4:raw_data[0].rfind(',')+10].strip()
		try:
			int(zip_code)
		except:
			if "Brighton Rehabilitation" in location_name:
				state = "PA"
				city = raw_data[1][raw_data[1].find(',')+1:raw_data[1].find(state)].strip()
				zip_code =  raw_data[1][raw_data[1].rfind(' ')+1:].strip()
		if "Suite" in city:
			street_address = street_address + " " + city[:city.find(',')]
			city = city[city.rfind(" "):].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[(\d)]{5} [\d]{3}-[\d]{4}", item.text)[0]
		except:
			phone = "<MISSING>"

		try:
			map_link = item.find('a')['href']
			req = session.get(map_link, headers = headers)
			time.sleep(randint(1,2))
			maps = BeautifulSoup(req.text,"lxml")
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			if "%" in raw_gps:
				latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
				longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
			else:
				latitude = raw_gps[raw_gps.rfind("=")+1:raw_gps.rfind(",")].strip()
				longitude = raw_gps[raw_gps.rfind(",")+1:].strip()

			if len(latitude) < 4 or len(latitude) > 13:
				try:
					driver.get(map_link)
					time.sleep(randint(6,8))
					try:
						map_link = driver.current_url
						at_pos = map_link.rfind("@")
						latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
						longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
					except:
						latitude = "<INACCESSIBLE>"
						longitude = "<INACCESSIBLE>"
				except:
					latitude = "<MISSING>"
					longitude = "<MISSING>"
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = raw_data[-1].replace("\n"," ").replace("\xa0","").strip()
		try:
			location_type = re.findall("\(.+\)", hours_of_operation)[0][1:-1]
		except:
			location_type = "<MISSING>"

		if "<" in hours_of_operation:
			hours_of_operation = hours_of_operation[:hours_of_operation.find("<")].strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		if not hours_of_operation:
			hours_of_operation = raw_data[-2].replace("\n"," ").replace("\xa0","").strip()
			hours_of_operation = re.sub(' +', ' ', hours_of_operation)
		print(hours_of_operation)
		
		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
