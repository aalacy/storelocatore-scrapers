from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time

from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.stantonoptical.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	all_links = []
	results = base.find(class_="location-list location-list-ajax").find_all("li")

	for result in results:
		link = result.find("a")['href']
		if "myeyelab.com" in link:
			link = "https://www.myeyelab.com/locations/" + "".join(link.split("/")[-2:])
		if link not in all_links:
			all_links.append(link)

	data = []
	total_links = len(all_links)

	driver = get_driver()
	time.sleep(2)

	for i, link in enumerate(all_links):
		print("Link %s of %s" %(i+1,total_links))
		time.sleep(randint(1,2))

		if "myeyelab.com" in link:
			# Use driver

			driver.get(link)
			print(link)
			time.sleep(randint(8,10))

			try:
				raw_data = driver.find_element_by_class_name("_1XdaXXRo7cD62gX-e8AxMt").text.split("\n")
				locator_domain = "myeyelab.com"
			except:
				# Get basic info from main page
				link = base_link
				locator_domain = "stantonoptical.com"

				item = results[i]
				location_name = item.find("h2").text.strip()
				print(location_name)

				raw_data = str(item)
				raw_data = raw_data[raw_data.find("</h4>")+6:raw_data.find("<br/>Distance")].split("<br/>")
				
				street_address = raw_data[0].strip()
				city_line = raw_data[1].strip()
				city = city_line[:city_line.find(',')].strip()
				state = city_line[city_line.find(',')+1:city_line.rfind(' ')].strip()
				zip_code = city_line[city_line.rfind(' ')+1:].strip()
				country_code = "US"
				try:
					phone = raw_data[2]
				except:
					phone = "<MISSING>"

				store_number = "<MISSING>"
				location_type = "<MISSING>"

				latitude = "<MISSING>"
				longitude = "<MISSING>"

				hours_of_operation = "<MISSING>"

				data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
				continue

			location_name = raw_data[0]
			print(location_name)

			street_address = raw_data[1]
			city = raw_data[2][:raw_data[2].find(',')].strip()
			state = raw_data[2][raw_data[2].find(',')+1:raw_data[2].rfind(' ')].strip()
			zip_code = raw_data[2][raw_data[2].rfind(' ')+1:].strip()
			country_code = "US"
			try:
				phone = raw_data[4]
				if "Store" in phone:
					item = results[i]
					raw_data = str(item)
					raw_data = raw_data[raw_data.find("</h4>")+6:raw_data.find("<br/>Distance")].split("<br/>")
					phone = raw_data[2]
			except:
				phone = "<MISSING>"

			location_type = "<MISSING>"

			driver.find_element_by_css_selector(".fas.fa-chevron-right").click()
			time.sleep(randint(2,3))
			driver.find_element_by_css_selector("._27ULr73zB8pnPloXgw7_Xj.fas.fa-caret-down").click()
			time.sleep(randint(2,3))
			hours_of_operation = driver.find_element_by_css_selector("._2g5ur5hcnExQwaQypj4Ujs").text.replace("\n"," ").strip()

			try:
				raw_gps = driver.find_element_by_xpath("//*[(@title='Open this area in Google Maps (opens a new window)')]").get_attribute("href")
				latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
				longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"

		else:
			# Use requests
			req = session.get(link, headers = HEADERS)
			time.sleep(randint(1,2))

			try:
				item = BeautifulSoup(req.text,"lxml")
				print(link)
			except (BaseException):
				print('[!] Error Occured. ')
				print('[?] Check whether system is Online.')

			locator_domain = "stantonoptical.com"
			location_name = item.find('h1').text.strip()
			print(location_name)

			street_address = item.find(class_="ss-p").text.strip()
			city_line = item.find_all(class_="ss-p")[1].text.strip()
			city = city_line[:city_line.find(',')].strip()
			state = city_line[city_line.find(',')+1:city_line.rfind(' ')].strip()
			zip_code = city_line[city_line.rfind(' ')+1:].strip()
			country_code = "US"
			store_number = "<MISSING>"
			try:
				phone = item.find(class_='phone').text.strip()
			except:
				phone = "<MISSING>"

			location_type = "<MISSING>"
			raw_hours = item.find(class_="week-hours").text.strip()
			hours_of_operation = raw_hours.replace("y","y ").replace("M","M ").replace("M onday","Monday").replace(" -","-")

			try:
				raw_gps = item.find(class_="s-directions hidden-md hidden-lg").a['href']
				latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
				longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()