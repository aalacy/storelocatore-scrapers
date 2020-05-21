import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
import phonenumbers
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
	states = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH",'OK',"OR","PA","RI","SC","SD",'TN',"TX","UT","VT","VA","WA","WV","WI","WY"]
	addresses = []
	locator_domain = 'https://www.metromarket.net/'

	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	}
	for state in states:
		# print(state)
		r = session.get("https://www.metromarket.net/stores/search?searchText="+str(state), headers=headers)
		soup = BeautifulSoup(r.text, "lxml")
		# json_data = json.loads(soup.find(lambda tag: (tag.name == "script") and "window.__INITIAL_STATE__ =" in tag.text).text.split("JSON.parse('")[1].split(',"contentHash"')[0].replace("Valentine\\'s","Valentine's").replace("What\'s","What's").replace(':"/"}]}}',':"/"}]}}}}}').replace("\\",""))['storeSearch']['storeSearchReducer']
		str1 = '{"stores":'+soup.find(lambda tag: (tag.name == "script") and "window.__INITIAL_STATE__ =" in tag.text).text.split('"stores":')[1].split(',"shouldShowFuelMessage":true}')[0]+"}"
		json_data = json.loads(str1.replace("\\",""))
		# print(json_data)
		# print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		
	##### store
	
		datas = json_data['stores']
		for key in datas:

			try:
				location_type = key["banner"]+" store"
			except:
				location_type = "store"
			
			location_name = key['vanityName']
			street_address = key['address']['addressLine1'].capitalize()
			# if "950 s george mason dr" in street_address:
			# 	print(key)
			city = key['address']['city'].capitalize()
			state = key['address']['stateCode']
			zipp =  key['address']['zip']
			country_code = key['address']['countryCode']
			store_number = key['storeNumber']
			if key['phoneNumber']:
				phone = phonenumbers.format_number(phonenumbers.parse(str(key['phoneNumber']), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
			else:
				phone = "<MISSING>"
			# location_type = "store"
			latitude = key['latitude']
			longitude = key['longitude']  
			# for hr in key['ungroupedFormattedHours']:
			#         hours_of_operation= " Sun - Sat:" +" "+hr['displayHours']
			page_url = "https://www.metromarket.net/stores/details/"+str(key['divisionNumber'])+"/"+str(store_number)
			# hours_of_operation = ""
			# for day_hours in key["ungroupedFormattedHours"]:
			# 	hours_of_operation += day_hours["displayName"] +  " = " + day_hours["displayHours"] + "  "
			
			
			try:
				r2 = session.get(page_url, headers=headers)
				soup2 = BeautifulSoup(r2.text, "lxml")
				script =json.loads(soup2.find(lambda tag:(tag.name == "script") and "openingHours" in tag.text).text)
				if script["openingHours"]:
					hours_of_operation = " ".join(script["openingHours"])
				elif script["department"][0]["openingHours"]:
					hours_of_operation = " ".join(script["department"][0]["openingHours"])
				else:
					hours_of_operation = "<MISSING>"
					# print("page_url")
				# hours_of_operation = " ".join(json.loads(soup3.find(lambda tag:(tag.name == "script") and "openingHours" in tag.text).text)['openingHours'])
			except:
				hours_of_operation = "<MISSING>"
				# print("except ==== ",page_url)
			# print(hours_of_operation)

			store = []
			store.append(locator_domain if locator_domain else '<MISSING>')
			store.append(location_name if location_name else '<MISSING>')
			store.append(street_address if street_address else '<MISSING>')
			store.append(city if city else '<MISSING>')
			store.append(state if state else '<MISSING>')
			store.append(zipp if zipp else '<MISSING>')
			store.append(country_code if country_code else '<MISSING>')
			store.append(store_number if store_number else '<MISSING>')
			store.append(phone if phone else '<MISSING>')
			store.append(location_type if location_type else '<MISSING>')
			store.append(latitude if latitude else '<MISSING>')
			store.append(longitude if longitude else '<MISSING>')
			store.append(hours_of_operation if hours_of_operation else "<MISSING>")
			store.append(page_url)
			# duplicate =str(store[1])+" "+str(store[2])+" "+str(store[3])+" "+str(store[4])+" "+str(store[5])+" "+str(store[6])+" "+str(store[7])+" "+str(store[8])+" "+str(store[9])+" "+str(store[10])+" "+str(store[11])+" "+str(store[12])+" "+str(store[13])
					
			if str(store[-1]) in addresses:
				continue
			addresses.append(str(store[-1]))
			# print("data = " + str(store))
			# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',)
			yield store

	########### fuel
		datas1 = json_data['fuel']
		for key1 in datas1:
			try:
				location_type = key["banner"]+" fuel"
			except:
				location_type = "fuel"
			# print(location_type)
			location_name = key1['vanityName']
			street_address = key1['address']['addressLine1'].capitalize()
			city = key1['address']['city'].capitalize()
			state = key1['address']['stateCode']
			zipp =  key1['address']['zip']
			country_code = key1['address']['countryCode']
			store_number = key1['storeNumber']
			phone = key1['phoneNumber']
			# location_type = "fuel"
			latitude = key1['latitude']
			longitude = key1['longitude']
			hours_of_operation = ''
			page_url = "https://www.metromarket.net/stores/details/"+str(key1['divisionNumber'])+"/"+str(store_number)
			# hours_of_operation = ""
			# for day_hours in key1["ungroupedFormattedHours"]:
			# 	hours_of_operation += day_hours["displayName"] +  " = " + day_hours["displayHours"] + "  "
			try:
				r3 = session.get(page_url, headers=headers)
				soup3 = BeautifulSoup(r3.text, "lxml")
				script =json.loads(soup3.find(lambda tag:(tag.name == "script") and "openingHours" in tag.text).text)
				if script["openingHours"]:
					hours_of_operation = " ".join(script["openingHours"])
				elif script["department"][0]["openingHours"]:
					hours_of_operation = " ".join(script["department"][0]["openingHours"])
				else:
					hours_of_operation = "<MISSING>"
					# print("page_url")
				# hours_of_operation = " ".join(json.loads(soup3.find(lambda tag:(tag.name == "script") and "openingHours" in tag.text).text)['openingHours'])
			except:
				hours_of_operation = "<MISSING>"
			# 	print("except ==== ",page_url)
			# print(hours_of_operation)

			store = []
			store.append(locator_domain if locator_domain else '<MISSING>')
			store.append(location_name if location_name else '<MISSING>')
			store.append(street_address if street_address else '<MISSING>')
			store.append(city if city else '<MISSING>')
			store.append(state if state else '<MISSING>')
			store.append(zipp if zipp else '<MISSING>')
			store.append(country_code if country_code else '<MISSING>')
			store.append(store_number if store_number else '<MISSING>')
			store.append(phone if phone else '<MISSING>')
			store.append(location_type if location_type else '<MISSING>')
			store.append(latitude if latitude else '<MISSING>')
			store.append(longitude if longitude else '<MISSING>')
			store.append(hours_of_operation if hours_of_operation else '<MISSING>')
			store.append(page_url)
			# duplicate =str(store[1])+" "+str(store[2])+" "+str(store[3])+" "+str(store[4])+" "+str(store[5])+" "+str(store[6])+" "+str(store[7])+" "+str(store[8])+" "+str(store[9])+" "+str(store[10])+" "+str(store[11])+" "+str(store[12])+" "+str(store[13])
			
			if str(store[-1]) in addresses:
				continue
			addresses.append(str(store[-1]))

			# print("data = " + str(store))
			# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',)
			yield store

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
