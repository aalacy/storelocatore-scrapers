from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
from random import randint
import time
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	last_page = 50
	for page_num in range(1,last_page):
		if page_num < last_page+1:
			link = "https://parknationalbank.com/about/locations/page/" + str(page_num)
			print(link)

			req = session.get(link, headers=headers)
			time.sleep(randint(2,4))
			try:
				base = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				print ('[!] Error Occured. ')
				print ('[?] Check whether system is Online.')

			if page_num == 1:
				last_page = int(base.find_all(class_="page-numbers")[-2].text)

			items = base.find_all(class_="row no-ng-margin")
			
			for item in items:
				locator_domain = "parknationalbank.com"
				location_name = item.h4.text.strip()
				print (location_name)

				raw_address = item.find(class_="branch-address").text.strip().replace("\t ",",").replace("\t","").split(",")
				if len(raw_address) == 5:
					street_address = (raw_address[0] + raw_address[1]).strip()
				else:
					street_address = raw_address[0]

				city = raw_address[-3].strip()
				state = raw_address[-2][:-6].strip()
				zip_code = raw_address[-2][-6:].strip()
				country_code = "US"
				store_number = "<MISSING>"
				phone = raw_address[-1].strip()
				location_type = "<MISSING>"

				# Maps
				map_link = item.find(class_="links").a['href']

				req = session.get(map_link, headers = headers)
				time.sleep(randint(1,2))
				try:
					maps = BeautifulSoup(req.text,"lxml")
				except (BaseException):
					print('[!] Error Occured. ')
					print('[?] Check whether system is Online.')

				try:
					raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
					latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
					longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
				except:
					latitude = "<MISSING>"
					longitude = "<MISSING>"
				if latitude == "37.6":
					latitude = "<MISSING>"
					longitude = "<MISSING>"

				try:
					hours_of_operation = item.find(class_="default-txt weekdays-txt").text.strip()
				except:
					hours_of_operation = "<MISSING>"

				data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
		else:
			break

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
