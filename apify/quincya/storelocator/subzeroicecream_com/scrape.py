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

	base_link = "https://www.subzeroicecream.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')
	
	section = base.findAll('div', attrs={'class': 'viewport'})[1]
	items = section.findAll('gb-carousel-pane', attrs={'class': 'ng-star-inserted'})

	if len(items) == 4:
		links = [
				"https://www.subzeroicecream.com/find-location/i/34446014/nashua-nh-sub-zero-nitrogen-ice-cream",
				"https://www.subzeroicecream.com/find-location/i/34446150/virginia-beach-va-sub-zero-nitrogen-ice-cream",
				"https://www.subzeroicecream.com/find-location/i/34445957/hunt-valley-md-sub-zero-ice-cream",
				"https://www.subzeroicecream.com/find-location/i/34446012/columbia-md-sub-zero-nitrogen-ice-cream"
				]
		data = []
		for link in links:			
			req = requests.get(link, headers=headers)

			try:
				base = BeautifulSoup(req.text,"lxml")
			except (BaseException):
				print ('[!] Error Occured. ')
				print ('[?] Check whether system is Online.')

			section = base.find('div', attrs={'class': 'content-container'})
						
			locator_domain = "subzeroicecream.com"		
			location_name = section.find('h1').text.strip()
			print (location_name)

			street_address = section.find('h3', attrs={'class': 'address ng-star-inserted'}).text.strip()
			street_address = street_address[:street_address.rfind(" ")].strip()
			city = location_name[:location_name.find(",")]
			state = location_name[location_name.find(",")+1:location_name.find(",")+4].strip()
			zip_code = "<MISSING>"
			country_code = "US"
			store_number = "<MISSING>"
			phone = base.find('ul', attrs={'class': 'buttons'}).a['href']
			phone = phone[phone.find(":")+1:]
			location_type = "<MISSING>"
			latitude = base.find('meta', attrs={'property': 'place:location:latitude'})['content']
			longitude = base.find('meta', attrs={'property': 'place:location:longitude'})['content']
			hours_of_operation = "<MISSING>"

			data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
