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

	base_url="https://www.marshalls.com"
	location_url ="https://www.marshalls.com/us/store/stores/allStores.jsp"
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
	pages=[]
	
	driver = get_driver()
	driver_page = get_driver()
	driver.get(location_url)
	time.sleep(6)
	links=driver.find_elements_by_xpath('/html/body/div[3]/div/div/div[1]/section/div[3]/div')
	for ls in links:	
		link=ls.find_elements_by_tag_name('a')
		for l in link:
			pages.append(l.get_attribute('href'))	
	
	for p in pages:
		while True:
			try:
				driver_page.get(p)
				time.sleep(6)
			except: 
				continue
			#print(p)
			locs.append(driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/section/section/input[3]').get_attribute('value'))
			streets.append(driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/section/section/form/div[4]/div[1]').text.split('\n')[0])
			try:
				cities.append(driver_page.find_element_by_xpath('/html/head/meta[13]').get_attribute('content').split(	'/')[-3].split('-')[-3].replace('+',' '))
			except:
				cities.append("<MISSING>")
			try:
				states.append(driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/section/div/div[1]/h1').text.split(', ')[1])
			except:
				states.append("<MISSING>")
			try:
				zips.append(p.split('/')[-3].split('-')[-1].replace('%20',''))
			except:
				zips.append("<MISSING>")
			try:
				ids.append(driver_page.find_element_by_xpath('/html/head/meta[13]').get_attribute('content').split('/')[-2])
			except:
				ids.append("<MISSING>")
			try:
				phones.append(driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/section/div/div[2]/div[1]/div[4]').text)
			except:
				phones.append("<MISSING>")
			try:
				timing.append(driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/section/div/div[2]/div[1]/div[1]').text
				+' '+driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/section/div/div[2]/div[1]/div[2]').text.replace('\n',' '))
				types.append(driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[5]/div/div/ul/li[1]/span').text+' '+
				driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[5]/div/div/ul/li[2]/span').text+' '+
				driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[5]/div/div/ul/li[3]/span').text+' '+
				driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[5]/div/div/ul/li[4]/span').text)
			except:
				timing.append("<MISSING>")
			try:
				lats.append(driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/section/section/input[1]').get_attribute('value'))
			except:
				lats.append("<MISSING>")
			try:
				longs.append(driver_page.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/section/section/input[2]').get_attribute('value'))
			except:
				longs.append("<MISSING>")
			break
			
						
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
