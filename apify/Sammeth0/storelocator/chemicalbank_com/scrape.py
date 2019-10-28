import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import ast

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

# Begin scraper
	locs = []
	streets = []
	states=[]
	cities = []
	types=[]
	phones = []
	zips = []
	longs = []
	lats = []
	timing = []
	ids=[]
	page_url=[]
	
	driver = get_driver()
	driver.get('https://www.chemicalbank.com/Locations')
	
	stores=driver.find_elements_by_tag_name('script')
	locations=stores[24].get_attribute('text').split('RenderData = ')[1].split(';')[0]
	locations_dict=ast.literal_eval(locations)
	locator_domain='https://www.chemicalbank.com/'
	country_code='US'
	page_url='https://www.chemicalbank.com/Locations'
	
	for i in range(len(locations_dict['LocationData'])):
		locs.append(locations_dict['LocationData'][i]['FullName'])
		streets.append((' ').join(locations_dict['LocationData'][i]['Address'].split(' ')))
		cities.append(locations_dict['LocationData'][i]['City'])
		states.append(locations_dict['LocationData'][i]['State'])
		zips.append(locations_dict['LocationData'][i]['PostalCode'])
		ids.append(locations_dict['LocationData'][i]['LocationID'])
		phones.append(locations_dict['LocationData'][i]['PhoneNumber'])
		lats.append(locations_dict['LocationData'][i]['Latitude'])
		longs.append(locations_dict['LocationData'][i]['Longitude'])
		
	
	data = []
	for i in range(len(locations_dict['LocationData'])):
		row = []
		row.append(locator_domain)
		row.append(locs[i] if locs[i] else "<MISSING>")
		row.append(streets[i] if streets[i] else "<MISSING>")
		row.append(cities[i] if cities[i] else "<MISSING>")
		row.append(states[i] if states[i] else "<MISSING>")
		row.append(zips[i] if zips[i] else "<MISSING>")
		row.append(country_code)
		row.append(ids[i] if ids[i] else "<MISSING>")
		row.append(phones[i] if phones[i] else "<MISSING>")
		row.append('ATM' if locations_dict['LocationData'][i]['FullName'].find("ATM") else 'Branch')
		row.append(lats[i] if lats[i] else "<MISSING>")
		row.append(longs[i] if longs[i] else "<MISSING>")
		row.append("<INACCESSIBLE>") 
		row.append(page_url)
		
		data.append(row)
	
    # End scraper
	
	driver.quit()
	return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
