import requests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
		
	base_link = "https://joansonthird.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'feature-column-text rte-setting marginTop15'})

	data = []
	for item in items:
		locator_domain = "joansonthird.com"
		try:
			location_name = item.find('h3').text.strip()
		except:
			continue
		print (location_name)
		
		raw_data = str(item.p).replace('<p>',"").replace('</p>',"").replace('\n',"").replace(',',"").split('<br/>')
		street_address = raw_data[0].strip()
		city = raw_data[1][:raw_data[1].rfind(' ')-3].strip()
		state = raw_data[1][raw_data[1].rfind(' ')-3:raw_data[1].rfind(' ')].strip()
		zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[\d]{3}.[\d]{3}.[\d]{4}", str(item))[0]
		except:
			phone = "<MISSING>"
		location_type = "<MISSING>"

		if location_name == "Studio City":
			raw_gps = "https://www.google.com/maps/place/12059+Ventura+Pl,+Studio+City,+CA+91604,+USA/@34.1448112,-118.3967849,17z/data=!3m1!4b1!4m5!3m4!1s0x80c2bdfd0da03909:0xac5b87916c389233!8m2!3d34.1448112!4d-118.3945962"
		else:
			raw_gps = item.findAll('a', attrs={'class': 'underlined_hover'})[2]['href']

		start_point = raw_gps.find("@") + 1
		latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
		long_start = raw_gps.find(',',start_point)+1
		longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
		try:
			int(latitude[4:8])
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"
		hours_of_operation = "<MISSING>"

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
