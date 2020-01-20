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
	location_url ="https://stores.partycity.com/"
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
	country_codes=['us','ca']
	
	for i in country_codes:
		location_name="https://stores.partycity.com/"
		driver.get(location_url+i)
		time.sleep(5)
		links=driver.find_elements_by_xpath('/html/body/div[1]/div[5]/div[3]/div/div/div')
		for ls in links:	
			country_code.append(i)
			print(country_code)
			link=ls.find_element_by_tag_name('a').get_attribute('href')
			print(link)
			pages_links.append(link)	
	print(pages_links)
	print(len(pages_links))
	
	for pl in pages_links:
		driver_page.get(pl)
		time.sleep(4)
		loc_links=driver_page.find_elements_by_xpath('/html/body/div[1]/div[5]/div[1]/div[1]/div/div[2]/div[3]/div/div')
		for ll in loc_links:
			loc_link=ll.find_element_by_tag_name('a').get_attribute('href')
			pages_locs.append(loc_link)
			print(ll)
	print(pages_locs)
	print(len(pages_locs))
	
	for lp in pages_locs:
		driver_loc.get(lp)
		time.sleep(4)
		try:
			page_loc=driver_loc.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div[1]/div/div[2]/div[3]/div/div').find_element_by_tag_name('a').get_attribute('href')
			pages.append(page_loc)
		except:
			continue
		print(page_loc)
		
		print(pages)
	print(len(pages))	
	
	for p in pages:
		driver.get(p)
		time.sleep(4)
		locs.append(driver.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/span').text)
		print(locs)
		print(len(locs))
		streets.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/span').text)
		print(streets)
		cities.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]').text.split(',')[0])
		print(cities)
		states.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]').text.split(',')[1].split(' ')[-2])
		print(states)
		zips.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]').text.split(',')[1].split(' ')[-1])
		print(zips)
		ids.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]').text.split('# ')[1])
		print(ids)
		try:
			phones.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/a').text)
		except:
			phones.append("<MISSING>")
		print(phones)
		timing.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[5]/div[1]/div/div[2]/div/div[2]').text.replace('\n',' '))
		print(timing)
		types.append("<MISSING>")
		lats.append(driver_page.find_element_by_xpath('/html/body/div[1]/script[13]'))
		print(lats)
		longs.append(driver_page.find_element_by_xpath('/html/body/div[1]/script[13]'))
		print(longs)

			
						
	return_main_object = []	
	for l in range(len(locs)):
		row = []
		row.append(base_url)
		row.append(locs[l])
		row.append(streets[l])
		row.append(cities[l])
		row.append(states[l])
		row.append(zips[l])
		row.append(country_code[l])
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
