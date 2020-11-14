import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sgzip import DynamicGeoSearch, SearchableCountries
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bylinebank_com')
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
        ## -------BRANCH --------##
	headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
			  }
	base_url = "https://www.bylinebank.com"
	locator_domain = base_url
	r = session.get("https://www.bylinebank.com/sitemap/", headers = headers)
	soup = BeautifulSoup(r.text,"lxml")
	a = soup.find("div",{'id':'sitemap_locations','class':'html_sitemap'}).find("ul")
	link_list = []
	for link in a.find_all("a"):
                logger.info(f'Grabbing branch: {link["href"]}')
                r1= session.get(link["href"], headers = headers)
                z = []
                for i in r1:
                        z.append(str(i))
                z = ''.join(z)
                z = z.replace("'b'",'')
                latitude = z.split('"latitude":')[1].split(',')[0].replace("'b'",'').replace("'",'').strip()
                longitude = z.split('"longitude":')[1].split('}')[0].replace("'b'",'').replace("'",'').strip()
                soup1 = BeautifulSoup(r1.content,"lxml")
                try:
                        location_name = soup1.find("meta",{"content":True,'property':'og:title'})['content']
                except:
                        location_name = "<MISSING>"
                try:
                        address =soup1.find('span',{'class':'address'}).text
                        street_address = address.split(",")[0].strip()
                        city = address.split(",")[1].strip()
                        state = address.split(",")[-1].split(' ')[-2].strip()
                        zip1 = address.split(",")[-1].split(' ')[-1].strip()
                        country_code = "US"
                except:
                        pass
                try:
                        phone = soup1.find('a',{'class':'phone_number'})['href'].replace('tel:','')
                except:
                        phone = "<MISSING>"
                try:
                        hours_of_operation = " ".join(list(soup1.find(lambda tag: (tag.name == "h4" ) and "Lobby Hours" in tag.text).find_next("table").stripped_strings))
                except:
                        hours_of_operation = "<MISSING>"
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
                yield store

	addresses = []
	# conn = http.client.HTTPSConnection("guess.radius8.com")
	header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
			  "Content-Type":"application/x-www-form-urlencoded",
			   "Referer": "https://bylinebank.locatorsearch.com/index.aspx?s=FCS"
			  }
	
	search = DynamicGeoSearch(country_codes=[SearchableCountries.USA], max_search_results = 100, max_radius_miles = 80)
	search.initialize()
	coords = search.next()
	current_results_len = 0
	# search.current_zip """"""""==zip
	
	while coords:
                lat, long = coords
                # try
                result_coords = []
                url = 'https://bylinebank.locatorsearch.com/GetItems.aspx'
                data = "address="+"&lat="+str(lat)+"&lng="+str(long)+"&searchby=ATMSF%7C&SearchKey=&rnd=1569844320549"
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
                items = 0
                for i in range(len(address1)):
                        street_address = address1[i].text
                        city = add2[i].text.split(",")[0]
                        state = add2[i].text.replace(",,",",").split(",")[1].split( )[0]
                        
                        zip1 = add2[i].text.replace(",,",",").split(",")[1].split( )[1]
                        if "<b>" in add2[i].text:
                                phone = add2[i].text.split("<b>")[1].replace("</b>","").strip()
                        else:
                                phone = "<MISSING>"
                        # logger.info(name[i])
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
                                items += 1
                                continue
                        addresses.append(store[2])

                        # logger.info("data = " + str(store))
                        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        yield store
                search.update_with(result_coords)
                logger.info(f'Coordinates remaining: {search.zipcodes_remaining()}; Last request yields {len(result_coords)-items} stores.')
                coords = search.next()
                
        



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
	# 	# logger.info(name[i])
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
	# 	logger.info("data=="+str(store1))
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
	# 	# logger.info(name[i])
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
	# 	logger.info("data == ",str(store2))

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
