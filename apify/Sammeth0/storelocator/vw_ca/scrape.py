import requests
from bs4 import BeautifulSoup
from lxml import html
import csv
import re


def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
	locs = []
	street = []
	states=[]
	cities = []
	types=[]
	phones = []
	zips = []
	long = []
	lat = []
	storeno = []
	page_url=[]
	
	page_url="https://www.vw.ca/app/dccsearch/vw-ca/en/Volkswagen%20Dealer%20Search/+/53.835794350000015/-95.32055685/4/+/+/+/+"
	r = requests.get(page_url)
	soup=BeautifulSoup(r.text,'lxml')
	
	stores=soup.findAll('script')[3].text.split('DD/MM/YYYY%22,%22LL%22:%22D%20MMMM%20YYYY%22,%22LLL%22:%22D%20MMMM%20YYYY%20LT%22,%22LLLL%22:%22dddd%20D%20MMMM%20YYYY%20LT%22,%22LT%22:')[1].split('%22copy%22:%22You%20are%20about%20to%20access%20a%20link%20which%20navigates%20you%20outside%20our%20application')[0]

	cities_pos=[m.start() for m in re.finditer('%22city%22:%22', stores)]
	zips_pos=[m.start() for m in re.finditer('%22postalCode%22:%22', stores)]
	lat_long_pos=[m.start() for m in re.finditer('%22geoPosition%22:%7B%22coordinates%22:%5B', stores)]
	phones_pos=[m.start() for m in re.finditer('%22phoneNumber%22:%22', stores)]
	addresses_pos=[m.start() for m in re.finditer('%22address%22:%7B%22street%22:%22', stores)]
	names_pos=[m.start() for m in re.finditer('%22name%22:%22', stores)]
	states_pos=[m.start() for m in re.finditer('%22province%22:%22', stores)]
	types_pos=[m.start() for m in re.finditer('%22type%22:%22Point%22%7D,%22services%22:%5B%22', stores)]
	ids_pos=[m.start() for m in re.finditer('%22id%22:%22', stores)]
	
	for i in names_pos:
		locs.append(stores[i:].split('%22name%22:%22')[1].split('%22,')[0].replace('%20',' '))
	for i in addresses_pos:
		street.append(stores[i:].split('%22address%22:%7B%22street%22:%22')[1].split('%22,')[0].replace('%20',' ').replace('%C3%A9','e').replace('H%C3%B4','o'))
	for i in cities_pos:
		cities.append(stores[i:].split('%22city%22:%22')[1].split('%22,')[0].replace('%20',' '))
	for i in states_pos:	
		states.append(stores[i:].split('%22province%22:%22')[1].split('%22,')[0].replace('%20',' '))
	for i in zips_pos:
		zips.append(stores[i:].split('%22postalCode%22:%22')[1].split('%22%7D')[0].replace('%20',' '))
	for i in ids_pos:
		storeno.append(stores[i:].split('%22id%22:%22')[1].split('%22,')[0])
	for i in phones_pos:
		phones.append(stores[i:].split('%22phoneNumber%22:%22')[1].split('%22,')[0])
	for i in types_pos:
		types.append(stores[i:].split('%22type%22:%22Point%22%7D,%22services%22:%5B%22')[1].split(',%22departments')[0].replace(',%22SERVICE%22,',' ').replace(',','').replace('%22',' ').replace('%5D',''))
	for i in lat_long_pos:
		lat.append(stores[i:].split('%22geoPosition%22:%7B%22coordinates%22:%5B')[1].split(',')[0])
	for i in lat_long_pos:
		long.append(stores[i:].split('%22geoPosition%22:%7B%22coordinates%22:%5B')[1].split(',')[1].split('%5D,')[0].replace('%5D',''))	
	
	return_main_object=[]
	for i in range(0, len(cities)):
		store=[]
		store.append("https://www.vw.ca")
		store.append(locs[i] if locs[i] else "<MISSING>")
		store.append(street[i] if street[i] else "<MISSING>")
		store.append(cities[i] if cities[i] else "<MISSING>")
		store.append(states[i] if states[i] else "<MISSING>")
		store.append(zips[i] if zips[i] else "<MISSING>")
		store.append('CA')
		store.append(storeno[i] if storeno[i] else "<MISSING>")
		store.append(phones[i] if phones[i] else "<MISSING>")
		store.append(types[i] if types[i] else "<MISSING>" )
		store.append(lat[i] if lat[i] else "<MISSING>")
		store.append(long[i] if long[i] else "<MISSING>")
		store.append('<MISSING>')
		store.append(page_url) 	
		
		return_main_object.append(store) 		
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
