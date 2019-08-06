import requests
from bs4 import BeautifulSoup
import csv

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://fracturedprune.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print '[!] Error Occured. '
		print '[?] Check whether system is Online.'

	license = base.findAll('div', attrs={'class': 'location-container'})[1]
	license_type = license.find('h2').text
	legacy = base.findAll('div', attrs={'class': 'location-container'})[2]
	legacy_type = legacy.find('h2').text

	license_rows = license.findAll('div', attrs={'class': 'row'})
	legacy_rows = legacy.findAll('div', attrs={'class': 'row'})

	locator_domain = "fracturedprune.com"

	data = []
	def get_types(location_type,rows,data):
		for row in rows:
			location_name = row.find('a').text.encode('utf-8').strip()
			raw_data = row.find('span', attrs={'class': 'address'}).encode('utf-8').split('<br/>')
			street_address = raw_data[0][raw_data[0].find('>')+1:].replace("&amp;","&").strip()
			raw_data[1] = raw_data[1].strip()
			if "Suite" in raw_data[1]:
				raw_data[1] = raw_data[2]
			city = raw_data[1][:raw_data[1].find(',')].strip()
			state = raw_data[1][raw_data[1].find(',')+1:raw_data[1].rfind(' ')].strip()
			zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].replace("</span>","").strip()
			country_code = "US"
			store_number = "<MISSING>"
			phone = row.find('span', attrs={'class': 'phone'}).text.replace("Phone:", "").encode('utf-8').strip()

			link = row.find('a')['href']

			req = requests.get(link, headers=headers)

			try:
				page_base = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				print '[!] Error Occured. '
				print '[?] Check whether system is Online.'
			try:
				latitude = page_base.find('span', attrs={'class': 'latitude'}).text.encode('utf-8').strip()
				longitude = page_base.find('span', attrs={'class': 'longitude'}).text.encode('utf-8').strip()
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
			try:	
				hours_of_operation = page_base.find('ul', attrs={'class': 'hours_list'}).text.encode('utf-8').strip()
			except:
				hours_of_operation = "<MISSING>"
			if hours_of_operation == "":
				hours_of_operation = "<MISSING>"

			data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
			print "Got page details"

		return data
	data = get_types(license_type,license_rows,data)
	data = get_types(legacy_type,legacy_rows,data)
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()