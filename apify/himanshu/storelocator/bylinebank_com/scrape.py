import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
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
	addresses = []
	base_url = "https://www.bylinebank.com"
	locator_domain = base_url
	# conn = http.client.HTTPSConnection("guess.radius8.com")
	header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
			  "Content-Type":"application/x-www-form-urlencoded",
			   "Referer": "https://bylinebank.locatorsearch.com/index.aspx?s=FCS"
			  }
	
	search = sgzip.ClosestNSearch()
	search.initialize()
	MAX_RESULTS = 100
	MAX_DISTANCE = 80
	coords = search.next_coord()
	current_results_len = 0
	# search.current_zip """"""""==zip
	
	while coords:
		# try:
		result_coords = []
		url = 'https://bylinebank.locatorsearch.com/GetItems.aspx'
	   
		data = "address="+str(search.current_zip)+"&lat="+str(coords[0])+"&lng="+str(coords[1])+"&searchby=ATMSF%7C&SearchKey=&rnd=1569844320549"
		pagereq = session.post(url,data=data, headers=header)
		soup = BeautifulSoup(pagereq.text, 'html.parser')
		add2 = soup.find_all("add2")
		address1 = soup.find_all("add1")
		current_results_len = len(address1)
		loc = soup.find_all("marker")
		hours = soup.find_all("contents")
		name = soup.find_all("title")
		locator_domain = "https://www.bylinebank.com"
		store_number ="<MISSING>"
		location_type ='ATM'
		for i in range(len(address1)):
			street_address = address1[i].text
			city = add2[i].text.split(",")[0]
			state = add2[i].text.replace(",,",",").split(",")[1].split( )[0]
			
			zip1 = add2[i].text.replace(",,",",").split(",")[1].split( )[1]
			if "<b>" in add2[i].text:
				phone = add2[i].text.split("<b>")[1].replace("</b>","").strip()
			else:
				phone = "<MISSING>"
			# print(name[i])
			location_name = name[i].text.replace("<br>","").strip()
			page_url = "https://www.bylinebank.com/locator/"


			if len(zip1)==3 or len(zip1)==7:
				country_code = "CA"
			else:
				country_code = "US"
			
			soup_hour = BeautifulSoup(hours[i].text,'lxml')
			if soup_hour.find("table"):
				h = []
				for i in soup_hour.find("table"):
					h.append(i.text)

				hour = " ".join(h).replace(":"," : ").strip()
			else:
				hour = "<MISSING>"
			hours_of_operation = hour
			try:
				latitude = loc[i].attrs['lat']
				longitude = loc[i].attrs['lng']
			except:
				pass
			result_coords.append((latitude,longitude))
		   
			store = []
			store.append(locator_domain if locator_domain else '<MISSING>')
			store.append(location_name if location_name else '<MISSING>')
			store.append(street_address if street_address else '<MISSING>')
			store.append(city if city else '<MISSING>')
			store.append(state if state else '<MISSING>')
			store.append(zip1 if zip1 else '<MISSING>')
			store.append(country_code if country_code else '<MISSING>')
			store.append(store_number if store_number else '<MISSING>')
			store.append(phone if phone else '<MISSING>')
			store.append(location_type)
			store.append(latitude if latitude else '<MISSING>')
			store.append(longitude if longitude else '<MISSING>')
			store.append(hours_of_operation if hours_of_operation else '<MISSING>')
			store.append(page_url)
			if store[2] in addresses:
				continue
			addresses.append(store[2])

			# print("data = " + str(store))
			# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
			yield store

		if current_results_len < MAX_RESULTS:
			# print("max distance update")
			search.max_distance_update(MAX_DISTANCE)
		elif current_results_len == MAX_RESULTS:
			# print("max count update")
			search.max_count_update(result_coords)
		else:
			raise Exception("expected at most " + str(MAX_RESULTS) + " results")
	  
		coords = search.next_coord()
		
	## -------BRANCH --------##
	r = session.get("https://www.bylinebank.com/sitemap/",headers = header)
	soup = BeautifulSoup(r.text,"lxml")
	a = soup.find("li",class_="page_item page-item-3599 page_item_has_children").find("ul",class_="children")
	link_list = []
	for link in a.find_all("a"):
		# link_list.append(link["href"])
		if "changeisgood" not in link["href"]:
			r1= session.get(link["href"],headers = header)
			soup1 = BeautifulSoup(r1.text,"lxml")
			try:
				location_name = soup1.find("div",{"id":"stage"}).h1.text.strip()
				div = soup1.find("div",{"id":"stage"})
				address =list(div.find("h2").stripped_strings)
				if len(address) > 1:
					street_address = address[0].strip()
					city = address[1].split(",")[0].strip()
					if len(address[1].split(",")) > 1:
						state = address[1].split(",")[-1].split()[0].strip()
						zip1 = address[1].split(",")[-1].split()[-1].strip()
					else:
						state = address[-2]
						zip1 = address[-1]
				country_code = "US"
				phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(div.find("h2").nextSibling.nextSibling.text.strip()))
				if phone_list:
					phone = phone_list[0]
				else:
					phone= "<MISSING>"
				hours_of_operation = " ".join(list(soup1.find(lambda tag: (tag.name == "h2" ) and "Lobby Hours" in tag.text).find_next("table").stripped_strings))
				latitude = soup1.find("iframe")["src"].split("!2d")[1].split("!2m")[0].split("!3d")[0].strip()
				longitude = soup1.find("iframe")["src"].split("!2d")[1].split("!2m")[0].split("!3d")[-1].strip()
				page_url = link["href"]
				location_type = "BRANCH"
				store_number ="<MISSING>"
				store = []
				store.append(locator_domain if locator_domain else '<MISSING>')
				store.append(location_name if location_name else '<MISSING>')
				store.append(street_address if street_address else '<MISSING>')
				store.append(city if city else '<MISSING>')
				store.append(state if state else '<MISSING>')
				store.append(zip1 if zip1 else '<MISSING>')
				store.append(country_code if country_code else '<MISSING>')
				store.append(store_number if store_number else '<MISSING>')
				store.append(phone if phone else '<MISSING>')
				store.append(location_type)
				store.append(latitude if latitude else '<MISSING>')
				store.append(longitude if longitude else '<MISSING>')
				store.append(hours_of_operation if hours_of_operation else '<MISSING>')
				store.append(page_url)
				if store[2] in addresses:
					continue
				addresses.append(store[2])

				# print("data = " + str(store))
				# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
				yield store

				
			except Exception as e:
				continue




	# # BRANCH LOCATIONS ##
	# data = 'lat=41.828699&lng=-87.771381&searchby=FCS%7C&SearchKey=&rnd=1586590653061'
	# pagereq = session.post("https://bylinebank.locatorsearch.com/GetItems.aspx", data=data, headers=header)
	# soup = BeautifulSoup(pagereq.text, 'html.parser')
	# add2 = soup.find_all("add2")
	# address1 = soup.find_all("add1")
	# current_results_len = len(address1)
	# loc = soup.find_all("marker")
	# hours = soup.find_all("contents")
	# name = soup.find_all("title")
	# locator_domain = "https://www.bylinebank.com"
	# store_number ="<MISSING>"
	# location_type ='BRANCH'
	# for i in range(len(address1)):
	# 	street_address = address1[i].text
	# 	city = add2[i].text.split(",")[0]
	# 	state = add2[i].text.replace(",,",",").split(",")[1].split( )[0]
		
	# 	zip1 = add2[i].text.replace(",,",",").split(",")[1].split( )[1].split("<br>")[0]
	# 	if "<b>" in add2[i].text:
	# 		phone = add2[i].text.split("<b>")[1].replace("</b>","").strip()
	# 	else:
	# 		phone = "<MISSING>"
	# 	# print(name[i])
	# 	location_name = name[i].text.replace("<br>","")
	# 	page_url = "https://www.bylinebank.com/locator/"+location_name.lower().replace(" ","-").replace("/","-").strip()

	# 	if len(zip1)==3 or len(zip1)==7:
	# 		country_code = "CA"
	# 	else:
	# 		country_code = "US"
		
	# 	soup_hour = BeautifulSoup(hours[i].text,'lxml')
	# 	if soup_hour.find("table"):
	# 		h = []
	# 		for i in soup_hour.find("table"):
	# 			h.append(i.text)

	# 		hour = " ".join(h).replace(":"," : ").strip()
	# 	else:
	# 		hour = "<MISSING>"
	# 	hours_of_operation = hour
	# 	try:
	# 		latitude = loc[i].attrs['lat']
	# 		longitude = loc[i].attrs['lng']
	# 	except:
	# 		latitude = "<MISSING>"
	# 		longitude = "<MISSING>"
		
	# 	store1 = []
	# 	store1.append(locator_domain if locator_domain else '<MISSING>')
	# 	store1.append(location_name if location_name else '<MISSING>')
	# 	store1.append(street_address if street_address else '<MISSING>')
	# 	store1.append(city if city else '<MISSING>')
	# 	store1.append(state if state else '<MISSING>')
	# 	store1.append(zip1 if zip1 else '<MISSING>')
	# 	store1.append(country_code if country_code else '<MISSING>')
	# 	store1.append(store_number if store_number else '<MISSING>')
	# 	store1.append(phone if phone else '<MISSING>')
	# 	store1.append(location_type)
	# 	store1.append(latitude if latitude else '<MISSING>')
	# 	store1.append(longitude if longitude else '<MISSING>')
	# 	store1.append(hours_of_operation if hours_of_operation else '<MISSING>')
	# 	store1.append(page_url)
	# 	print("data=="+str(store1))
	# 	yield store1


	# # OFFICE LOCATIONS
	# data = 'lat=41.828699&lng=-87.771381&searchby=OFC%7C&SearchKey=&rnd=1585212256530'
	# pagereq = session.post("https://bylinebank.locatorsearch.com/GetItems.aspx", data=data, headers=header)
	# soup = BeautifulSoup(pagereq.text, 'html.parser')
	# add2 = soup.find_all("add2")
	# address1 = soup.find_all("add1")
	# current_results_len = len(address1)
	# loc = soup.find_all("marker")
	# hours = soup.find_all("contents")
	# name = soup.find_all("title")
	# locator_domain = "https://www.bylinebank.com"
	# store_number ="<MISSING>"
	# location_type ='OFFICE'
	# for i in range(len(address1)):
	# 	street_address = address1[i].text
	# 	city = add2[i].text.split(",")[0]
	# 	state = add2[i].text.replace(",,",",").split(",")[1].split( )[0]
		
	# 	zip1 = add2[i].text.replace(",,",",").split(",")[1].split( )[1].split("<br>")[0]
	# 	if "<b>" in add2[i].text:
	# 		phone = add2[i].text.split("<b>")[1].replace("</b>","").strip()
	# 	else:
	# 		phone = "<MISSING>"
	# 	# print(name[i])
	# 	location_name = name[i].text.replace("<br>","")
	# 	page_url = "https://www.bylinebank.com/locator/"+location_name.lower().replace(" ","-").replace("/","-").strip()

	# 	if len(zip1)==3 or len(zip1)==7:
	# 		country_code = "CA"
	# 	else:
	# 		country_code = "US"
		
	# 	soup_hour = BeautifulSoup(hours[i].text,'lxml')
	# 	if soup_hour.find("table"):
	# 		h = []
	# 		for i in soup_hour.find("table"):
	# 			h.append(i.text)

	# 		hour = " ".join(h).replace(":"," : ").strip()
	# 	else:
	# 		hour = "<MISSING>"
	# 	hours_of_operation = hour
	# 	try:
	# 		latitude = loc[i].attrs['lat']
	# 		longitude = loc[i].attrs['lng']
	# 	except:
	# 		pass
		
	# 	store2 = []
	# 	store2.append(locator_domain if locator_domain else '<MISSING>')
	# 	store2.append(location_name if location_name else '<MISSING>')
	# 	store2.append(street_address if street_address else '<MISSING>')
	# 	store2.append(city if city else '<MISSING>')
	# 	store2.append(state if state else '<MISSING>')
	# 	store2.append(zip1 if zip1 else '<MISSING>')
	# 	store2.append(country_code if country_code else '<MISSING>')
	# 	store2.append(store_number if store_number else '<MISSING>')
	# 	store2.append(phone if phone else '<MISSING>')
	# 	store2.append(location_type)
	# 	store2.append(latitude if latitude else '<MISSING>')
	# 	store2.append(longitude if longitude else '<MISSING>')
	# 	store2.append(hours_of_operation if hours_of_operation else '<MISSING>')
	# 	store2.append(page_url)
	# 	yield store2
	# 	print("data == ",str(store2))

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
