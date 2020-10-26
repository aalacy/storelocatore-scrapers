import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json




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
	addresses =[]
	locator_domain = base_url = "https://www.augustahealth.com/"

	r = session.get("https://www.ssmhealth.com/location-results/acupuncture?range=0&zip=11576&lat=40.7985&lng=-73.6476#locationResults")
	soup= BeautifulSoup(r.text,"lxml")
	# print(soup.prettify())
	for loc in soup.find("select",{"id":"specialtyLocType"}).find_all("option")[1:]:
		location_type = loc["value"].lower().replace(" ","-").strip()
		r1 =session.get("https://www.ssmhealth.com/location-results/"+str(location_type)+"?range=0&zip=11576&lat=40.7985&lng=-73.6476#locationResults")
		soup1 = BeautifulSoup(r1.text,"lxml")
		page_area= soup1.find("div",class_="PagerNumberArea")
		if page_area:
			page = page_area.find_all("a",class_="UnselectedPage")[-1].text.strip()
			page_no =1
			while True:

				# print(location_type)
				r2 = session.get("https://www.ssmhealth.com/location-results/"+str(location_type)+"?range=0&zip=11576&lat=40.7985&lng=-73.6476&page="+str(page_no))
				soup2 = BeautifulSoup(r2.text,"lxml")
				for loc_block in  soup2.find_all("div",class_="location-block LocationResult"):
					latitude = loc_block["data-lat"]
					longitude = loc_block["data-lng"]
					store_number = loc_block["data-locationid"]
					locjson = json.loads(loc_block.find("div",class_="locJSON").text)
					location_name = locjson["Name"]
					street_address = locjson["Address"]
					city = locjson["City"]
					state = locjson["State"]
					zipp = locjson["ZipCode"]
					country_code = "US"
					page_url = "https://www.ssmhealth.com/"+locjson["Link"]
					r3 = session.get(page_url)
					soup3 = BeautifulSoup(r3.text,"lxml")
					try:
						phone = soup3.find("a",class_="phone").text.strip()
					except:
						phone = "<MISSING>"
					try:
						hours_of_operation = " ".join(list(soup3.find("div",{"id":"SocDetailSection"}).find("div",class_="row pt-4").stripped_strings))
					except:

						hours_of_operation = "<MISSING>"
					store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
					store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
					if street_address in addresses:
						continue
					addresses.append(street_address)
					# print("data = " + str(store))
					# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
					store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
					yield store
				if page_no >= int(page):
					break
				
				page_no += 1

		else:
			# pass
			#print("https://www.ssmhealth.com/location-results/"+str(location_type)+"?range=0&zip=11576&lat=40.7985&lng=-73.6476#locationResults")
			r2 = session.get("https://www.ssmhealth.com/location-results/"+str(location_type)+"?range=0&zip=11576&lat=40.7985&lng=-73.6476")
			soup2 = BeautifulSoup(r2.text,"lxml")
			for loc_block in  soup2.find_all("div",class_="location-block LocationResult"):
				latitude = loc_block["data-lat"]
				longitude = loc_block["data-lng"]
				store_number = loc_block["data-locationid"]
				locjson = json.loads(loc_block.find("div",class_="locJSON").text)
				location_name = locjson["Name"]
				street_address = locjson["Address"]
				city = locjson["City"]
				state = locjson["State"]
				zipp = locjson["ZipCode"]
				country_code = "US"
				page_url = "https://www.ssmhealth.com/"+locjson["Link"]
				r3 = session.get(page_url)
				soup3 = BeautifulSoup(r3.text,"lxml")
				try:
					phone = soup3.find("a",class_="phone").text.strip()
				except:
					phone = "<MISSING>"
				try:
					hours_of_operation = " ".join(list(soup3.find("div",{"id":"SocDetailSection"}).find("div",class_="row pt-4").stripped_strings))
				except:

					hours_of_operation = "<MISSING>"
				store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
				store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
				if street_address in addresses:
					continue
				addresses.append(street_address)
				# print("data = " + str(store))
				# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
				store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
				yield store

	
	

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
