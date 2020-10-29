from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.terminix.com/exterminators/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	final_links = []
	main_links = []

	main_items = base.find_all(class_="c-directory-list-content-item-link")
	for main_item in main_items:
		main_link = base_link + main_item['href']
		if "/" in main_item['href']:
			final_links.append(main_link)
		else:
			main_links.append(main_link)
	
	for next_link in main_links:
		req = session.get(next_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		next_items = base.find_all(class_="c-directory-list-content-item")
		for next_item in next_items:
			link = base_link + next_item.find(class_="c-directory-list-content-item-link")['href']
			final_links.append(link)

	data = []
	for final_link in final_links:
		final_req = session.get(final_link, headers = HEADERS)
		item = BeautifulSoup(final_req.text,"lxml")

		locator_domain = "terminix.com"

		location_name = item.find(class_="NAP-locationName").text.strip()

		street_address = item.find(class_="c-address-street-1").text.replace("\u200b","").strip()
		try:
			street_address = street_address + " " + item.find(class_="c-address-street c-address-street-2").text.replace("\u200b","").strip()
			street_address = street_address.strip()
		except:
			pass
		street_address = street_address.replace("  "," ").strip()

		city = item.find('span', attrs={'itemprop': 'addressLocality'}).text.strip()
		state = item.find(class_="c-address-state").text.strip()
		zip_code = item.find(class_="c-address-postal-code").text.strip()
		country_code = "US"
		store_number = final_link.split("-")[-1]
		
		try:
			location_type = ",".join(list(item.find(class_="NAP-servicesList").stripped_strings))
		except:
			location_type = "<MISSING>"

		try:
			phone = item.find(class_="NAP-phone").a.text.strip()
		except:
			phone = "<MISSING>"

		latitude = item.find('meta', attrs={'itemprop': 'latitude'})['content']
		longitude = item.find('meta', attrs={'itemprop': 'longitude'})['content']

		hours_of_operation = ""
		raw_hours = item.find(class_="c-location-hours-details")
		raw_hours = raw_hours.find_all("td")

		hours = ""
		hours_of_operation = ""

		try:
			for hour in raw_hours:
				hours = hours + " " + hour.text.strip()
			hours_of_operation = (re.sub(' +', ' ', hours)).strip()
		except:
			pass
		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		location_data = [locator_domain, final_link, location_name, street_address, city, state, zip_code,
						country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

		data.append(location_data)

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
