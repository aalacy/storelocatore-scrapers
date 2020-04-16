import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import sgzip
import json
import time

session = SgRequests()

def write_output(data):
	with open('data.csv', mode='w',newline="") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)


def fetch_data():
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
		'accept': '*/*',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
	}
	locator_domain = base_url = "https://www.baptistonline.org/"
	addressesess= []
	main_arr=[]
	
	r = session.get("https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearchByType?query=11576&dsiID={32179276-CB99-4809-B92A-37738122FA0C}&locationType=Clinic&uniqueID=79bda440-e5ee-4f71-b0f6-8b4edb3d1d30&radius=5000&bmgonly=true&_=1587010148776")
	soup = BeautifulSoup(r.text,"lxml")
	for loc_list in soup.find("div",{"data-location-type":"Clinic"}).find_all("li",class_="row"):
		latitude = loc_list.find("input",{"name":"location-lat"})["value"]
		longitude = loc_list.find("input",{"name":"location-lng"})["value"]
		location_name = loc_list.find("p",class_="location-name").text.strip()
		address = list(loc_list.find("p",class_="location-address").stripped_strings)
		street_address = " ".join(address[:-1])
		city= address[-1].split(",")[0].strip()
		state = address[-1].split(",")[-1].split()[0].strip()
		zipp = address[-1].split(",")[-1].split()[-1].strip()
		country_code = "US"
		phone = loc_list.find("a",class_="location-phone").text.strip()
		location_type = "Clinic"
		store_number = "<MISSING>"
		hours_of_operation = "<MISSING>"
		page_url = "https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearchByType?query=11576&dsiID={32179276-CB99-4809-B92A-37738122FA0C}&locationType=Clinic&uniqueID=79bda440-e5ee-4f71-b0f6-8b4edb3d1d30&radius=5000&bmgonly=true&_=1587010148776"
		store = [locator_domain, location_name,street_address, city, state, zipp, country_code,
				store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
		store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
		main_arr.append(store)
	r2 = session.get("https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query=11576&dsiID={4F95E7DF-1E5F-4499-A7DE-B89F6AA1F5A0}&uniqueID=f5ee8665-b411-4904-b597-ee6b3b128330&radius=%203000&_=1587012202935")
	soup2 = BeautifulSoup(r2.text,"lxml")
	for loc_list in soup2.find("div",{"data-location-type":"Minor Medical"}).find_all("li",class_="row"):
		latitude = loc_list.find("input",{"name":"location-lat"})["value"]
		longitude = loc_list.find("input",{"name":"location-lng"})["value"]
		location_name = loc_list.find("p",class_="location-name").text.strip()
		address = list(loc_list.find("p",class_="location-address").stripped_strings)
		street_address = " ".join(address[:-1])
		city= address[-1].split(",")[0].strip()
		state = address[-1].split(",")[-1].split()[0].strip()
		zipp = address[-1].split(",")[-1].split()[-1].strip()
		country_code = "US"
		phone = loc_list.find("a",class_="location-phone").text.strip()
		location_type = "Minor Medical Centers"
		store_number = "<MISSING>"
		hours_of_operation = "<MISSING>"
		page_url = "https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query=11576&dsiID={4F95E7DF-1E5F-4499-A7DE-B89F6AA1F5A0}&uniqueID=f5ee8665-b411-4904-b597-ee6b3b128330&radius=%203000&_=1587012202935"
		store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
				store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
		store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
		main_arr.append(store)
	r3 = session.get("https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query=11576&dsiID={8A8B9B20-6D80-40E3-8F79-518BB364915F}&uniqueID=1a5cd54f-a5e4-4b61-80ab-9fca0586f035&radius=%203000&_=1587012202937")
	soup3 = BeautifulSoup(r3.text,"lxml")
	for loc_list in soup3.find("div",{"data-location-type":"Specialty"}).find_all("li",class_="row"):
		latitude = loc_list.find("input",{"name":"location-lat"})["value"]
		longitude = loc_list.find("input",{"name":"location-lng"})["value"]
		location_name = loc_list.find("p",class_="location-name").text.strip()
		address = list(loc_list.find("p",class_="location-address").stripped_strings)
		street_address = " ".join(address[:-1])
		city= address[-1].split(",")[0].strip()
		state = address[-1].split(",")[-1].split()[0].strip()
		zipp = address[-1].split(",")[-1].split()[-1].strip()
		country_code = "US"
		phone = loc_list.find("a",class_="location-phone").text.strip()
		location_type = "Speciality Facilities"
		store_number = "<MISSING>"
		hours_of_operation = "<MISSING>"
		page_url = "https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query=11576&dsiID={8A8B9B20-6D80-40E3-8F79-518BB364915F}&uniqueID=1a5cd54f-a5e4-4b61-80ab-9fca0586f035&radius=%203000&_=1587012202937"
		store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
				store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
		store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
		main_arr.append(store)
	
	r4 = session.get("https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query=11576&dsiID={03483C17-988E-4B89-9C70-57688C4EDAC3}&uniqueID=87baa463-dc15-4941-9889-c8b279a8e65e&radius=%203000&_=1587012989891")
	soup4 = BeautifulSoup(r4.text,"lxml")
	for loc_list in soup4.find("div",{"data-location-type":"Hospital"}).find_all("li",class_="row"):
		latitude = loc_list.find("input",{"name":"location-lat"})["value"]
		longitude = loc_list.find("input",{"name":"location-lng"})["value"]
		location_name = loc_list.find("p",class_="location-name").text.strip()
		address = list(loc_list.find("p",class_="location-address").stripped_strings)
		street_address = " ".join(address[:-1])
		city= address[-1].split(",")[0].strip()
		state = address[-1].split(",")[-1].split()[0].strip()
		zipp = address[-1].split(",")[-1].split()[-1].strip()
		country_code = "US"
		phone = loc_list.find("a",class_="location-phone").text.strip()
		location_type = "Hospital"
		store_number = "<MISSING>"
		hours_of_operation = "<MISSING>"
		page_url = "https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query=11576&dsiID={03483C17-988E-4B89-9C70-57688C4EDAC3}&uniqueID=87baa463-dc15-4941-9889-c8b279a8e65e&radius=%203000&_=1587012989891"
		store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
				store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
		store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
		main_arr.append(store)

	for data in range(len(main_arr)):
		if "Suite" in main_arr[data][2] or "Floor" in main_arr[data][2]:
			main_arr[data][2]=main_arr[data][2].split("Suite")[0].split("Floor")[0].replace(",",'')

		if str(main_arr[data][2]+main_arr[data][-5]) in addressesess:
			continue
		addressesess.append(str(main_arr[data][2]+main_arr[data][-5]))
		yield main_arr[data]
		# print("data = " + str(main_arr[data]))
		# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')



def scrape():
	data = fetch_data()
	write_output(data)

scrape()
