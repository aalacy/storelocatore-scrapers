import requests
from bs4 import BeautifulSoup
from lxml import html
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

	
	
	base_url ="https://www.centurynationalbank.com"
	return_main_object=[]
	location_names=[]
	bank_name=[]
	street_addresses=[]
	location_types=[]
	nums=[]
	hours=[]
	lats_lngs=[]
	soup=[]
	page_url=[]
	data = []
	
	locs = []
	streets= []
	states=[]
	cities = []
	types=[]
	phones = []
	zips = []
	longs = []
	lats = []
	timing = []
	ids=[]
	urls=[]
	
	for url in range(14):
		page_url.append("https://centurynationalbank.com/locations/page/"+str(url+1)+"/?place&latitude&longitude&type=location#038,latitude&longitude&type=location")
		soup.append(BeautifulSoup(requests.get(page_url[url]).text,'lxml'))
		location_names.append(soup[url].findAll(class_="sub-head fw-light"))
		street_addresses.append(soup[url].findAll(class_="branch-address fw-light"))
		location_types.append(soup[url].findAll(class_='large-4 columns'))
		nums.append(soup[url].findAll(class_="links fw-light"))
		hours.append(soup[url].findAll(class_="large-6 small-6 columns"))
		lats_lngs.append(soup[url].findAll(class_="medium-6 columns "))
		
		for i in range(len(location_names[url])):
			
			urls.append(page_url[url])
			if location_names[url][i].find("a")!=None:
				locs.append(location_names[url][i].a.text+' '+str(lats_lngs[url]).split('"parent_bank_name":"')[i+1].split('"')[0])
			else:
				locs.append(location_names[url][i].find("span").text+' '+str(lats_lngs[url]).split('"parent_bank_name":"')[i+1].split('"')[0])
			streets.append(street_addresses[url][i].contents[0].strip().replace('\n',''))
			cities.append(street_addresses[url][i].contents[2].split(',')[0].replace(',',' ').replace('\n',''))
			states.append(street_addresses[url][i].contents[2].split(',')[1].strip().split(' ')[0].replace(',',' ').replace('\n',''))
			zips.append(street_addresses[url][i].contents[2].split(',')[1].strip().split(' ')[1].replace(',',' ').replace('\n',''))
			ids.append(str(nums[url][i]).split('data-locationid="')[1].split('"')[0])
			if street_addresses[url][i].find("a")!=None:
				phones.append(street_addresses[url][i].a.get_text().replace(',',' ').replace('\n',''))
			else:
				phones.append("<MISSING>")
			types.append(location_types[url][i].text.replace(',',' ').replace('\n',''))
			lats.append(str(lats_lngs[url]).split('"lat":"')[i+1].split('"')[0])
			longs.append(str(lats_lngs[url]).split('"lng":"')[i+1].split('"')[0])
			try:
				timing.append(hours[url][i].text.replace(',',' ').replace('\n',''))
			except:
				timing.append("<MISSING>")
	
		
	for l in range(len(locs)):
		row = []
		row.append(base_url)
		row.append(locs[l] if locs[l] else "<MISSING>")
		row.append(streets[l] if streets[l] else "<MISSING>")
		row.append(cities[l] if cities[l] else "<MISSING>")
		row.append(states[l] if states[l] else "<MISSING>")
		row.append(zips[l] if zips[l] else "<MISSING>")
		row.append("US")
		row.append(ids[l] if ids[l] else "<MISSING>")
		row.append(phones[l] if phones[l] else "<MISSING>")
		row.append(types[l] if types[l] else "<MISSING>")
		row.append(lats[l] if lats[l] else "<MISSING>")
		row.append(longs[l] if longs[l] else "<MISSING>")
		row.append(timing[l] if timing[l] else "<MISSING>") 
		row.append(urls[l])
		
		data.append(row)
	
    # End scraper
	return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
