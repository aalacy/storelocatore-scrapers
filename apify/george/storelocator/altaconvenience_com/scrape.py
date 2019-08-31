import requests
from bs4 import BeautifulSoup
import csv
import sys

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
	url = 'http://altaconvenience.com/Find-a-Store'
	page = requests.get('http://altaconvenience.com/Find-a-Store')
	soup = BeautifulSoup(page.text, 'html.parser')
	locations = soup.find_all(class_ = 'location')
	allData = []
	for location in locations:
		details = location.get_text().split('\n')[:-1]
		details = [details[i].replace(' ','') for i in range(len(details))]
		if len(details) == 4:
			locator_domain = url
			locations_name = details[0]
			street_address = details[1]
			city = details[2].split('.')[0][:-2]
			state = details[2].split('.')[0][-2:]
			zip_code = details[2].split('.')[1]
			country_code= 'US'
			store_number= details[0][-4:]
			phone = details[-1]
			location = '<MISSING>'
			latitude = '<MISSING>'
			longitude = '<MISSING>'
			hours_of_operation = '<MISSING>'
			allData.append([locator_domain, locations_name, street_address, city, state, zip_code, country_code, store_number, phone, location, latitude, longitude, hours_of_operation])
	return allData	
	
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
