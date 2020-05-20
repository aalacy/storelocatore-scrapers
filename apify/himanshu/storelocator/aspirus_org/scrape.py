import csv
from bs4 import BeautifulSoup
import requests
from sgrequests import SgRequests
import time
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import platform
system = platform.system()

session = SgRequests()
def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if "linux" in system.lower():
        return webdriver.Firefox(executable_path='./geckodriver', options=options)        
    else:
        return webdriver.Firefox(executable_path='geckodriver.exe', options=options)


def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8",newline="") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)
def request_wrapper(url,method,headers,data=None):
	request_counter = 0
	if method == "get":
		while True:
			try:
				r = requests.get(url,headers=headers)
				return r
				break
			except:
				time.sleep(2)
				request_counter = request_counter + 1
				if request_counter > 10:
					return None
					break
	elif method == "post":
		while True:
			try:
				if data:
					r = requests.post(url,headers=headers,data=data)
				else:
					r = requests.post(url,headers=headers)
				return r
				break
			except:
				time.sleep(2)
				request_counter = request_counter + 1
				if request_counter > 10:
					return None
					break
	else:
		return None

def fetch_data():
	
	lat_list = []
	lng_list = []
	street_list =[]
	driver = get_driver()
	 # it will used in store data.
	addresses = []
	addresses1 = []
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
	}

	base_url = "https://www.aspirus.org"
	locator_domain = base_url
	r = request_wrapper("https://www.aspirus.org/find-a-location","get", headers=headers)
	soup = BeautifulSoup(r.text, "lxml")
	
	location_type_url_list = []
	for loc_type_soup in soup.find("div", {"class": "locations"}).find_all("div",{"class","view-all1"}):

		locator_domain = base_url
		location_type = ""

	#     # do your logic here.
		location_type = loc_type_soup.find("a").find("strong").text
		# print(location_type)
		loc_type_url = base_url + loc_type_soup.find("a")["href"]

		driver.get(loc_type_url)
			
		vk=10
		page = 2
		while True:
			page_v="Page "+str(page)
			# print(page_v)
			soup_loc_list = BeautifulSoup(driver.page_source, "lxml")
			split_latlng = soup_loc_list.text.split("myLatlng = new google.maps.LatLng(")
			
			for str_data in split_latlng[1:]:
				final_data = str_data.split("});")[0]
				lat_list.append(final_data.split(",")[0])
				lng_list.append(final_data.split(",")[1].split(")")[0])
				street_list.append(final_data.split("</strong><br />")[1].split("<br />")[0].strip())
			if soup_loc_list.find("ul", {"class": "results"}):
				for location in soup_loc_list.find("ul", {"class": "results"}).find_all("li",{"data-loc":True}):
				
					location_name = ""
					street_address = ""
					city = ""
					state = ""
					zipp = ""
					country_code = "US"
					store_number = ""
					phone = ""
					latitude = ""
					longitude = ""
					raw_address = ""
					hours_of_operation = ""
					page_url = ""

					page_url = base_url + location.find("a")["href"]
					store_number = page_url.split("-")[-1].strip()
					r_location = request_wrapper(page_url,"get", headers=headers)
					soup_location = BeautifulSoup(r_location.text, "lxml")
					full_address = list(soup_location.find("ul",{"class":"gen-info flex"}).stripped_strings)
					location_name = full_address[1]
					street_address = full_address[2].strip()
					for i in range(len(street_list)):
						if street_address == street_list[i]:
							latitude = lat_list[i]
							longitude = lng_list[i]
					street_address = full_address[2].split(",")[0].strip()
					phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))
					ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address))
					us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))
					state_list = re.findall(r'\b[A-Z]{2}\b', str(full_address))

					if ca_zip_list:
						zipp = ca_zip_list[-1]
						country_code = "CA"

					if us_zip_list:
						zipp = us_zip_list[-1]
						country_code = "US"

					if state_list:
						state = state_list[-1]

					if phone_list:
						phone = phone_list[0]
					map_it_index = full_address.index("Map It")
					city = full_address[:map_it_index][-1].split(",")[0].strip()
					# if "ET" == city:
					#     print(full_address)
					# .replace("Business  & Provider","").replace("Therapy","").replace("Clinic","").replace("Walk-In Care","").replace("Business","").replace("Provider","").replace("&","")
					if "Hours" in full_address:
						hours_of_operation = " ".join(full_address[full_address.index("Hours"):]).replace("Hours Business Office Hours","").replace('weekends and holidays Call 906 - 337 - 6500 and ask to contact Home Health "on - call." 24-hour emergency services are available','').replace("Medical Esthetician Consultations & Services By Appointment","").replace("Hours","").replace("Open for calls","").replace("(staffed)","").replace("Store","").replace("Visiting","").replace("(ET)","").replace("(support person, siblings anytime) Critical Care Unit Visitation Daily, anytime Family, significant others only","").replace("Family Birthplace Visitation","").replace("Visiting  Unlimited, but quiet hours after 8:30 pm (Hospital Entrance B closed on weekends) Scheduling","").replace("After-hours,","").replace("General","").replace("Unlimited, but quiet hours after 8:30 pm (Hospital Entrance B closed on weekends) Scheduling ","").replace("By Appointment","").replace("EST","").replace("Evenings By appointment","").strip()
					# print("full_address == ",full_address)

					if "Visit website for hours" in full_address:
						hours_of_operation="<MISSING>"
					if "Open by appointment" == hours_of_operation.strip():
						hours_of_operation = "<MISSING>"

					store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
							store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
					store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
					# if (str(store[-5])+" "+str(store[-7])) in addresses:
					# 	continue
					# addresses.append(str(store[-5])+" "+str(store[-7]))
					#print("data = " + str(store))
					#print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
					yield store
					# duplicate =str(store[1])+" "+str(store[2])+" "+str(store[3])+" "+str(store[4])+" "+str(store[5])+" "+str(store[6])+" "+str(store[7])+" "+str(store[8])+" "+str(store[10])+" "+str(store[11])+" "+str(store[12])+" "+str(store[13])
					
						
			if soup_loc_list.find("a",{"onclick":"$get('FormAction').value='ExecuteSearch';"}):
				if page-1 == vk:
					# print("vk === ", vk)
					vk +=10
					driver.find_element_by_xpath("//a[@title='"+str('Next 10')+"']").click()
				try:
					driver.find_element_by_xpath("//a[@title='"+str(page_v)+"']").click()
				except:
					break
				page += 1
			else:
				break
	driver.quit() 

	page_list=["https://www.aspirus.org/find-a-location/aspirus-rosewood-terrace-family-home-387","https://www.aspirus.org/find-a-location/aspirus-primrose-corner-family-home-386"]
	for page_url in page_list:
		r= session.get(page_url)
		soup_location = BeautifulSoup(r.text,"lxml")  
		store_number = page_url.split("-")[-1].strip()
		full_address = list(soup_location.find("ul",{"class":"gen-info flex"}).stripped_strings)
		location_name = full_address[1]
		street_address = full_address[2].strip()
		for i in range(len(street_list)):
			if street_address == street_list[i]:
				latitude = lat_list[i]
				longitude = lng_list[i]
		street_address = full_address[2].split(",")[0].strip()
		phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))
		ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address))
		us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))
		state_list = re.findall(r'\b[A-Z]{2}\b', str(full_address))

		if ca_zip_list:
			zipp = ca_zip_list[-1]
			country_code = "CA"

		if us_zip_list:
			zipp = us_zip_list[-1]
			country_code = "US"

		if state_list:
			state = state_list[-1]

		if phone_list:
			phone = phone_list[0]
		map_it_index = full_address.index("Map It")
		city = full_address[:map_it_index][-1].split(",")[0].strip()
		hours_of_operation = " ".join(full_address[full_address.index("Hours"):])
		location_type = "Senior Health & Adult Living"
		country_code = "US"
		store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
							store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
		store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
		
		#print("data = " + str(store))
		#print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
		yield store
def scrape():
	data = fetch_data()
	write_output(data)


scrape()


'''
Adult Living & Care Facilities - 7
Birthing Centers -6
Chiropractors -48
Clinics - Primary Care -47
Clinics - Specialty Care - 122
Clinics - Walk-In - 11
Dental & Oral Care -14
Dialysis Centers - 3
Emergency Care - 9
Eye Care - 37
Fitness Centers -4
Home Medical Equipment Stores -2 
Hospices -4
Hospitals - 10
Mental Health Treatment & Counseling - 63
Occupational Health Clinics -8
Pharmacies -4
Sleep Centers -7
Surgery Centers - 5
Therapy & Rehab -59
7+6+48+47+122+11+14+3+9+37+4+2+4+10+63+8+4+7+5+59 = 470



'''
