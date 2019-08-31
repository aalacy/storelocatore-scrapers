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

	base_link = "https://crazymocha.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.findAll('p', attrs={'style': 'white-space:pre-wrap;'})

	driver = get_driver()
	data = []
	num = 0
	for item in items:
		location_name = ""
		locator_domain = "crazymocha.com"
		if num == 0 or num == 2:
			num = num + 1
			continue
		if num == 3:
			location_name = "CORPORATE HEADQUARTERS"
			print (location_name)
			raw_data = str(item).replace('<p>',"").replace('</p>',"").replace('\n',"").replace('\xa0',"").split('<br/>')
			street_address = raw_data[0][raw_data[0].rfind(">")+1:raw_data[0].find(",")].strip()
			city = raw_data[0][raw_data[0].find(',')+1:raw_data[0].rfind(',')].strip()
			state = raw_data[0][raw_data[0].rfind(',')+1:raw_data[0].rfind(',')+4].strip()
			zip_code = raw_data[0][raw_data[0].rfind(',')+4:raw_data[0].rfind(',')+10].strip()
			country_code = "US"
			store_number = "<MISSING>"
			try:
				phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", item.text)[0]
			except:
				phone = "<MISSING>"
			location_type = "<MISSING>"
			latitude = "<MISSING>"
			longitude = "<MISSING>"
			hours_of_operation = "<MISSING>"
			data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
			num = num + 1
			continue
		if location_name == "":
			location_name = item.find('strong').text.strip()
			print (location_name)
			raw_data = str(item).replace('<p>',"").replace('</p>',"").replace('\n',"").replace('\xa0',"").split('<br/>')
			street_address = raw_data[1][raw_data[1].rfind(">")+1:raw_data[1].find(",")].strip()
			city = raw_data[1][raw_data[1].find(',')+1:raw_data[1].rfind(',')].strip()
			state = raw_data[1][raw_data[1].rfind(',')+1:raw_data[1].rfind(',')+4].strip()
			zip_code = raw_data[1][raw_data[1].rfind(',')+4:raw_data[1].rfind(',')+10].strip()
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
				phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", item.text)[0]
			except:
				phone = "<MISSING>"
			location_type = "<MISSING>"

			try:
				map_link =item.find('a')['href']
				driver.get(map_link)
				time.sleep(4)
				raw_gps = driver.current_url
				start_point = raw_gps.find("@") + 1
				latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
				long_start = raw_gps.find(',',start_point)+1
				longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"

			hours_of_operation = raw_data[2].replace("\n"," ").replace("\xa0","").strip()
			hours_of_operation = re.sub(' +', ' ', hours_of_operation)

			data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
			num = num + 1
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
