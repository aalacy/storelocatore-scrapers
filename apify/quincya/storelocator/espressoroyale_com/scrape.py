import requests
from bs4 import BeautifulSoup
import csv
import time
import re


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://espressoroyalecoffee.com/store-locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')

	locations = base.findAll('div', attrs={'class': 'img-with-aniamtion-wrap center'})

	data = []
	for location in locations:
		try:
			loc_link = location.a['href']
		except:
			continue

		req = requests.get(loc_link, headers=headers)

		try:
			loc_base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print ('[!] Error Occured. ')
			print ('[?] Check whether system is Online.')
		
		location_names = loc_base.findAll('h3')
		locator_domain = "espressoroyalecoffee.com"

		for loc in location_names:
			link = loc.a['href']
			print ('Getting link: ' + link)
			req = requests.get(link, headers=headers)

			try:
				new_base = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				print ('[!] Error Occured. ')
				print ('[?] Check whether system is Online.')
			
			location_name = new_base.find('h2').text
			section = new_base.find('div', attrs={'class': 'wpb_row vc_row-fluid vc_row inner_row standard_section'})
			raw_data = str(section.findAll('div', attrs={'class': 'wpb_text_column wpb_content_element'})[0].p).replace("<p>","").replace("</p>","").replace("\n","").split('<br/>')
			street_address = raw_data[0]
			city = raw_data[1][:raw_data[1].find(',')].strip()
			state = raw_data[1][raw_data[1].find(',')+1:raw_data[1].rfind(' ')].strip()
			zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].strip()
			country_code = "US"
			store_number = "<MISSING>"
			phone = re.findall("[[\d]{3}.[\d]{3}.[\d]{4}", section.text)[0]	
			location_type = "<MISSING>"
			hours_of_operation = section.findAll('div', attrs={'class': 'wpb_text_column wpb_content_element'})[1].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").replace("Hours:","").strip()
			hours_of_operation = re.sub(' +', ' ', hours_of_operation)

			raw_gps = new_base.find('iframe')['src']
			start_point = raw_gps.find("2d") + 2
			longitude = raw_gps[start_point:raw_gps.find('!',start_point)]
			long_start = raw_gps.find('!',start_point)+3
			latitude = raw_gps[long_start:raw_gps.find('!',long_start)]
			try:
				int(latitude[4:8])
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"

			data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation,link])
			print ('Got page details')
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()