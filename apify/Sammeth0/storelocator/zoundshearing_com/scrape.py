import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd
import csv


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
	locations=[]
	data=[]
	
	locator_domain ="https://www.zoundshearing.com"
	country_code="US"
	
	urlpage = 'https://www.zoundshearing.com/corp/storelocator/' 
	options = Options()
	options.headless = True
	driver = webdriver.Firefox(firefox_options=options, executable_path = 'C:/Users/user/Desktop/Odetta/Sammeth0/storelocator/zoundshearing_com/geckodriver')
	driver = webdriver.Firefox()
	driver.get(urlpage)
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
	time.sleep(3)
	
	locs_results = driver.find_elements_by_xpath(".//span[@class='location_name']")
	for r in locs_results:
		locs.append(r.text)
	
	streets_results = driver.find_elements_by_xpath(".//div[@class='results_row_center_column location_secondary']")
	for r in streets_results:
		streets.append(r.find_element_by_xpath(".//span[@class='slp_result_address slp_result_street']").text)
		cities.append(r.find_element_by_xpath(".//span[@class='slp_result_address slp_result_citystatezip']").text.split(',')[0])
		states.append(r.find_element_by_xpath(".//span[@class='slp_result_address slp_result_citystatezip']").text.split(', ')[1].split(' ')[0])
		zips.append(r.find_element_by_xpath(".//span[@class='slp_result_address slp_result_citystatezip']").text.split(' ')[-1])
		id=r.find_element_by_xpath(".//span[@class='slp_result_address slp_result_street2']").text.split(' ')[-1]
		if id!='':
			ids.append(id)
		else:
			ids.append("<MISSING>")
		try:
			phones.append(r.find_element_by_xpath(".//span[@class='slp_result_address slp_result_phone']").text)
		except:
			phones.append("<MISSING>")
	timing_results=driver.find_elements_by_xpath(".//div[@class='results_row_right_column location_tertiary']")
	for r in timing_results:
		timing.append(r.find_element_by_xpath(".//span[@class='slp_result_contact slp_result_hours']").text)
		directions=r.find_element_by_xpath(".//span[@class='slp_result_contact slp_result_directions']/a").get_attribute('href')
		driver_directions= webdriver.Firefox(firefox_options=options, executable_path = 'C:/Users/user/Desktop/Odetta/Sammeth0/storelocator/zoundshearing_com/geckodriver')
		driver_directions = webdriver.Firefox()
		driver_directions.get(directions)
		driver_directions.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
		lats.append(str(driver_directions.find_elements_by_xpath(".//meta")[8].get_attribute('content')).split('center=')[1].split('%2C')[0])
		longs.append(str(driver_directions.find_elements_by_xpath(".//meta")[8].get_attribute('content')).split('%2C')[1].split('&zoom')[0])

	return_main_object=[]
	for i in range(len(locs)):
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
		row.append("<MISSING>")
		row.append(lats[i] if lats[i] else "<MISSING>")
		row.append(longs[i] if longs[i] else "<MISSING>")
		row.append(timing[i] if timing[i] else "<MISSING>") 
		row.append(urlpage)
		
		return_main_object.append(row)
	driver.quit()
	return return_main_object
	

def scrape():
    data = fetch_data()
    write_output(data)

scrape()