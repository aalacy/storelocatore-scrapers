import requests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "http://supersupermarket.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.findAll('li')
	data = []
	for item in items:
		locator_domain = "supersupermarket.com"
		country_code = "US"
		store_number = "<MISSING>"
		phone = re.findall("[[\d]{3} [\d]{3} [\d]{4}", item.text)[0]
		location_type = "<MISSING>"
		hours_of_operation = (item.findAll("p")[2].text + item.findAll("p")[3].text).replace("  ", " ").strip()

		link = "http://supersupermarket.com/" + item.a['href']
		link = link.replace('home','contact-us')

		req = requests.get(link, headers=headers)
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')

		location_name = base.find('meta', attrs={'property': 'og:title'})['content']
		#print (location_name)

		raw_gps = base.find('iframe')['src']
		start_point = raw_gps.find("2d") + 2
		longitude = raw_gps[start_point:raw_gps.find('!',start_point)]
		long_start = raw_gps.find('!',start_point)+3
		latitude = raw_gps[long_start:raw_gps.find('!',long_start)]
		try:
			int(latitude[4:8])
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		req = requests.get(raw_gps, headers=headers)
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')

		raw_data = str(base)
		start_point = raw_data.find("Super Supermarket",1000)
		raw_line = raw_data[start_point+18:raw_data.find("United",start_point)-2].strip()
		street_address = raw_line[:raw_line.find(",")].strip()
		city = raw_line[raw_line.find(",")+1:raw_line.rfind(',')].strip()
		state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation,link])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
