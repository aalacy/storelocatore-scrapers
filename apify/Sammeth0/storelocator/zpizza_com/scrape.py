import requests
from bs4 import BeautifulSoup
from lxml import html
import csv


def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

	us_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
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
	pages=[]
	
	locator_domain ="http://zpizza.com"
	country_code="US"
	page_url="http://zpizza.com/search-locations?for=f"
		
	r = requests.get(page_url)
	soup=BeautifulSoup(r.text,'lxml')

	all_divs=soup.findAll(class_="vcard location open")
	for all_div in all_divs:
		divs=all_div.findAll(class_="location-contact")
		coming_soon=all_div.find(class_="coming-soon")
		if coming_soon==None:
			for div in divs:
				state=div.find(class_='region').text.replace('\xa0','')
				if state in us_states:
					locs.append(div.find(class_='locality').text)
					streets.append(div.find(class_='street-address').text)
					cities.append(div.find(class_='locality').text)
					states.append(div.find(class_='region').text)
					zips.append(div.find(class_='postal-code').text)
					id=str(div.find(class_='street-address').text).split('#')
					try:
						ids.append(id[1])
					except:
						ids.append("<MISSING>")
					phone=str(div.find('a',href=True,text=True))
					if phone != 'None':
						phones.append( phone.split('href="tel:')[1].split('">')[0])
					else:
						phones.append("<MISSING>")
			locations=all_div.findAll(class_='fn location-name')
			for location in locations:
				if location.find(class_="taproom-location"):
					types.append(soup.find("dd").text)
				else:
					types.append("<MISSING>")
			
			longs_lats=soup.findAll(class_='vcard location open')
			for long_lat in longs_lats:
				longs.append(long_lat['data-geo'].split(',')[0])
				lats.append(long_lat['data-geo'].split(',')[1])
			
			details= all_div.findAll(class_='details')
			for detail in details:
				a=locator_domain+detail.find('a')['href']
				r_timing= requests.get(a)
				soup_timing=BeautifulSoup(r_timing.text,'lxml')
				timing.append((' '.join(str(soup_timing.find(class_='hours-of-operation')).split('<dt>')[1:])).replace('<dt>',' ')
				.replace('<dd>',' ').replace('</dt>','').replace('</dd>','').replace('</dl>',''))
		
	#print(streets)
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
		row.append(types[i] if types[i] else "<MISSING>")
		row.append(lats[i] if lats[i] else "<MISSING>")
		row.append(longs[i] if longs[i] else "<MISSING>")
		row.append(timing[i] if timing[i] else "<MISSING>") 
		row.append(page_url)
		
		return_main_object.append(row)
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
