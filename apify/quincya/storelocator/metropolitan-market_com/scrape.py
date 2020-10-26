from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
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
	
	base_link = "https://metropolitan-market.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	session = SgRequests()

	req = session.get(base_link, headers=headers)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')
	
	items = base.findAll('div', attrs={'class': 'feature_box'})

	data = []
	for item in items:
		if "Coming Soon" in item.text:
			continue

		link = "https://metropolitan-market.com" + item.a['href']

		req = session.get(link, headers=headers)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')

		locator_domain = "metropolitan-market.com"
		location_name = base.find('h3').text.strip() + " - " + base.find('h2').text.strip()
		print (location_name)
		section = base.find('div', attrs={'class': 'section_col_content'}).p
		raw_data = str(section).replace('<p>',"").replace('</p>',"").replace('\n',"").split('<br/>')
		street_address = raw_data[0].strip()
		city = raw_data[1][:raw_data[1].rfind(',')].strip()
		state = raw_data[1][raw_data[1].rfind(',')+1:raw_data[1].rfind(' ')].strip()
		zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", str(base))[0]
		except:
			phone = "<MISSING>"
		location_type = "<MISSING>"

		map_link = base.find('a', attrs={'class': 'button'})['href']
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
		if "=" in latitude:
			latitude = latitude[latitude.rfind("=")+1:latitude.rfind(",")].strip()
			longitude = latitude[latitude.rfind(",")+1:].strip()

		hours = str(base.findAll('div', attrs={'class': 'section_col_content'})[1]).replace('<p>',"").replace('</p>',"").replace('\n',"").replace('</div>',"").split('<br/>')
		hours_of_operation = hours[-1][hours[-1].rfind(">")+1:]

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
