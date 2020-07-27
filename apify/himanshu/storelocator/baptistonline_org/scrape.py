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

	l_type = {"0":"Clinic","1":"Minor Medical Centers","2":"Speciality Facilities","3":"Hospital"}
	locator_domain = "https://www.baptistonline.org/"
	addressesess= []
	l_url = [
		"https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearchByType?query=38017&dsiID={32179276-CB99-4809-B92A-37738122FA0C}&locationType=Clinic&uniqueID=79bda440-e5ee-4f71-b0f6-8b4edb3d1d30&radius=5000&bmgonly=true&contextid={09646042-A7F0-424E-A508-E6E3178E3C16}&_=1595841861300",
		"https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query=38017&dsiID={4F95E7DF-1E5F-4499-A7DE-B89F6AA1F5A0}&uniqueID=f5ee8665-b411-4904-b597-ee6b3b128330&radius=%203000&contextid={4968632C-2AC9-427F-86B2-11CF3B32C5D4}&_=1595842100608",
		"https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query=38017&dsiID={8A8B9B20-6D80-40E3-8F79-518BB364915F}&uniqueID=1a5cd54f-a5e4-4b61-80ab-9fca0586f035&radius=%203000&contextid={703258BD-5DDD-4264-9BCA-22FB4ABC2196}&_=1595842100610",
		"https://www.baptistonline.org/api/sitecore/LocationsFolder/LocationsListingSearch?query=38017&dsiID={03483C17-988E-4B89-9C70-57688C4EDAC3}&uniqueID=87baa463-dc15-4941-9889-c8b279a8e65e&radius=%203000&contextid={58E9A999-CF83-4FEB-8E37-48E6F4D08CE5}&_=1595842100607"
	]	
	
	for index in range(len(l_url)):
		soup = BeautifulSoup(session.get(l_url[index]).content,"lxml")
		for loc_list in soup.find_all("li",class_="row"):
			latitude = loc_list.find("input",{"name":"location-lat"})["value"]
			longitude = loc_list.find("input",{"name":"location-lng"})["value"]
			location_name = loc_list.find("p",class_="location-name").text.strip()
			try:
				if "www.google.com/maps" not in loc_list.find("a",{"aria-label":re.compile("View Baptist")})['href']:
					page_url = loc_list.find("a",{"aria-label":re.compile("View Baptist")})['href']

					if "http" in page_url:
						page_url = page_url
					elif "/locations" in page_url:
						page_url = "https://www.baptistonline.org" + page_url
					else:
						page_url = "https://www.baptistonline.org" + page_url

				else:
					page_url = "<MISSING>"
			except:
				page_url = "<MISSING>"
			address = list(loc_list.find("p",class_="location-address").stripped_strings)
			street_address = " ".join(address[:-1])
			city= address[-1].split(",")[0].strip()
			state = address[-1].split(",")[-1].split()[0].strip()
			zipp = address[-1].split(",")[-1].split()[-1].strip()
			country_code = "US"
			phone = loc_list.find("a",class_="location-phone").text.strip()
			location_type = l_type[str(index)]
			store_number = "<MISSING>"
			hours_of_operation = "<MISSING>"
			if "Suite" in street_address or "Floor" in street_address or "Ste" in street_address or "#" in street_address:
				street_address = street_address.split("Suite")[0].split("Floor")[0].split("Ste")[0].split("#")[0].replace(",",'')
			
			store = [locator_domain, location_name,street_address, city, state, zipp, country_code,
					store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
			store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
			
			if store[2] in addressesess:
				continue
			addressesess.append(store[2])

			yield store


def scrape():
	data = fetch_data()
	write_output(data)

scrape()
