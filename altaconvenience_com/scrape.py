import requests
from bs4 import BeautifulSoup
import pprint
url = 'http://altaconvenience.com/Find-a-Store'
page = requests.get('http://altaconvenience.com/Find-a-Store')
soup = BeautifulSoup(page.text, 'html.parser')

locations = soup.find_all(class_ = 'location')
refinedLocations = {}
for location in locations:
	details = location.get_text().split('\n')[:-1]
	details = [details[i].replace(' ','') for i in range(len(details))]
	if len(details) == 4:
		material = {
		'locator_domain': url,
		'locations_name': details[0],
		'street_address': details[1],
		'city': details[2].split('.')[0][:-2],
		'state': details[2].split('.')[0][-2:],
		'zip': details[2].split('.')[1],
		'country_code': 'US',
		'store_number': details[0][-4:],
		'phone': details[-1],
		'location': '<MISSING>',
		'latitude': '<MISSING>',
		'hours_of_operation': '<MISSING>'
		}
		try:
			refinedLocations[location.find('a').get_text()] = material
		except:
			print('This isn\'t a store')


pprint.pprint(refinedLocations)