import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import ast
import time
import urllib.request

def get_driver():
	options = Options()
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('--window-size=1920,1080')
	options.add_argument("user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'")
	return webdriver.Chrome('chromedriver', options=options)

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
	locations=[]
	driver = get_driver()
	driver_hours = get_driver()
	driver.get('https://www.chemicalbank.com/Locations')

	time.sleep(4)
	stores=driver.find_elements_by_tag_name('script')
	
	for i in range(len(stores)):
		if (len(stores[i].get_attribute('text').split('RenderData = '))==2):
			locations=stores[i].get_attribute('text').split('RenderData = ')[1].split(';')[0]
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
		driver_hours.get('https://www.chemicalbank.com/LocationDataByID/'+str(ids[i]))
		time.sleep(3)
		#print('https://www.chemicalbank.com/LocationDataByID/'+str(ids[i]))
		hours_dict=ast.literal_eval(driver_hours.find_element_by_tag_name('body').text)
		#print(hours_dict)
		try:
			days_count=str(hours_dict).split('"Name":"')[2].count('"DayName"')
		except:
			days_count=0
		types_count=str(hours_dict).split('Features')[1].count('"Name":"')
		timing_location=''
		
		for i in range(1,days_count):
			days=str(hours_dict).split('"Name":"')[2].split('"DayName":"')[i].split('"')[0]
			TimeOpen=str(hours_dict).split('"Name":"')[2].split('"TimeOpen":"')[i].split('"')[0]
			TimeClose=str(hours_dict).split('"Name":"')[2].split('"TimeClose":"')[i].split('"')[0]
			timing_location=timing_location+' '+days+' '+TimeOpen+' '+TimeClose
			#print(timing_location)
		if timing_location=='':
			timing.append("<MISSING>")
		else:
			timing.append(timing_location)
		type=''
		for j in range(1,types_count+1):
			type=type+' '+str(hours_dict).split('"Name":"')[j+1].split('"')[0]
		types.append(type)
		phone=str(hours_dict).split('"PhoneNumber":"')[1].split('"')[0].strip()
		if phone=='':
			phones.append("<MISSING>")
		else:
			phones.append(phone)	
		#print(phone)
		lat=str(hours_dict).split('"Latitude":"')[1].split('"')[0]
		if lat=='':
			lats.append("<MISSING>")
		else:
			lats.append(lat)
		#print(lat)
		long=str(hours_dict).split('"Longitude":"')[1].split('"')[0]
		if long=='':
			longs.append("<MISSING>")
		else:
			longs.append(long)
		#print(long)
		
		
	
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
		row.append(types[i] if types[i] else "<MISSING>")
		row.append(lats[i] if lats[i] else "<MISSING>")
		row.append(longs[i] if longs[i] else "<MISSING>")
		row.append(timing[i] if timing[i] else "<MISSING>")
		row.append(page_url)
		
		data.append(row)
	
    # End scraper
	
	return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()