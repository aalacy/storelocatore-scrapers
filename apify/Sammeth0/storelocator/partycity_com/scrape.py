import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import csv
import time 
import re 

def get_driver():
	options = Options()
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('--window-size=1920,1080')
	options.add_argument("user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'")
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

	base_url="https://www.partycity.com"
	location_url ="https://stores.partycity.com"
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
	country_code=[]
	pages_links=[]
	pages_locs=[]
	pages=[]
	
	driver = get_driver()
	driver_page = get_driver()
	driver_loc = get_driver()
	driver_store = get_driver()
	#country_codes=['us']
	
	#for i in country_codes:
	location_name="http://stores.partycity.com/us/"
	driver.get(location_name)
	time.sleep(5)
	links=driver.find_elements_by_xpath('/html/body/div[1]/div[5]/div[3]/div/div/div')
	for ls in links:	
		country_code.append("us")
		link=ls.find_element_by_tag_name('a').get_attribute('href')
		pages_links.append(link)	
	
	for pl in pages_links:
		driver_page.get(pl)
		time.sleep(10)
		loc_links=driver_page.find_elements_by_xpath('/html/body/div[1]/div[5]/div[1]/div[1]/div/div[2]/div[3]/div/div')
		for ll in loc_links:
			loc_link=ll.find_element_by_tag_name('a').get_attribute('href')
			pages_locs.append(loc_link)
	
	for lp in pages_locs:
		driver_loc.get(lp)
		time.sleep(10)
		page_loc=driver_loc.find_elements_by_xpath('/html/body/div[1]/div[5]/div[1]/div[1]/div/div[2]/div[3]/div/div')
		for pl in page_loc:
			pages.append(pl.find_element_by_tag_name('a').get_attribute('href'))
		
	
	for p in pages:
		driver_store.get(p)
		time.sleep(15)
		locs.append(driver_store.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/span').text)	
		streets.append(driver_store.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[1]').text)
		cities.append(driver_store.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]').text.split(',')[0])
		states.append(driver_store.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]').text.split(',')[1].split(' ')[-2])
		zips.append(driver_store.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]').text.split(',')[1].split(' ')[-1])	
		try:
			ids.append(driver_store.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]').text.replace('#','').replace('Store','').strip())
		except:
			ids.append("<MISSING>")		
		try:
			phones.append(driver_store.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/a').text)
		except:
			phones.append("<MISSING>")
		try:
			timing.append(driver_store.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[2]/div/div[2]/div[4]').text.replace('\n',' '))
		except:
			timing.append("<MISSING>")
		types.append("<MISSING>")
		try:
			lats.append(driver_store.find_element_by_xpath('/html/body/div[1]/script[13]').get_attribute('innerHTML').split('"latitude": "')[1].split('"')[0])
		except:
			lats.append("<MISSING>")		
		try:
			longs.append(driver_store.find_element_by_xpath('/html/body/div[1]/script[13]').get_attribute('innerHTML').split('"longitude": "')[1].split('"')[0])
		except:
			longs.append("<MISSING>")	
	
						
	return_main_object = []	
	for l in range(len(locs)):
		row = []
		row.append(base_url)
		row.append(locs[l])
		row.append(streets[l])
		row.append(cities[l])
		row.append(states[l])
		row.append(zips[l])
		row.append("US")
		row.append(ids[l])
		row.append(phones[l])
		row.append(types[l])
		row.append(lats[l])
		row.append(longs[l])
		row.append(timing[l]) 
		row.append(pages[l])
		
		return_main_object.append(row)
	
    # End scraper
	driver.quit()
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
