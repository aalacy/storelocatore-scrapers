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
	base_url ="https://www.bluefcu.com"
	page_url="https://www.bluefcu.com/locations-and-hours"
	longlat_url="https://www.bluefcu.com/locations-and-hours/map"
	return_main_object=[]
	r = requests.get(page_url)
	rll=requests.get(longlat_url)
	soup=BeautifulSoup(r.text,'lxml')
	soupll=BeautifulSoup(rll.text,'lxml')
	divs=soup.findAll(class_="accordion__pane js-accordion__pane")
	for div in divs:
		location_names=div.find("h3")
		name=location_names.text
		cities=div.find(class_="dual-column__col1")
		address=cities.h4.text.split('\n')[0].strip()
		city=cities.h4.text.split('\n')[1].split(',')[0].strip()
		state=cities.h4.text.split('\n')[1].split(',')[1].strip()
		zip=cities.h4.text.split('\n')[1].split(',')[2].strip()
		phone=cities.p.contents[0]
		atms=div.find(class_="branch-location__24-hr-services")
		atm=atms.findAll(class_="branch-location__service")
		location_type=''
		for a in atm:
			no_atm=a.find(class_='error fa fa-times-circle')
			type_a=a.text.strip().replace('\n',' ').replace(':',' ')
			if (no_atm==None):
				location_type=location_type+type_a
		branchs=soup.find(class_="branch-location__special-services")
		branch=branchs.findAll(class_="branch-location__service")
		for b in branch:
			no_branch=b.find(class_='error fa fa-times-circle')
			type_b=b.text.strip().replace('\n',' ').replace(':',' ')
			if (no_branch==None):
				location_type=location_type+type_b
		hour=cities.find(class_='branch-location__hours').text.strip().replace('\n',' ').replace(',',' ')
		ll=str(soupll.find(class_="map__data location-marker-data")).find(name.split(' ')[0])
		if ll==-1:
			lat="<MISSING>"
			lng="<MISSING>"
		else:
			data_lat=str(soupll.find(class_="map__data location-marker-data"))[0:ll].rfind('data-lat="')
			data_long=str(soupll.find(class_="map__data location-marker-data"))[0:ll].rfind('data-long="')
			lat=str(soupll.find(class_="map__data location-marker-data"))[data_lat:ll].split('data-lat="')[1].split('"')[0]
			lng=str(soupll.find(class_="map__data location-marker-data"))[data_long:ll].split('data-long="')[1].split('"')[0]
		country='US'
		store=[]
		store.append(base_url)
		store.append(name.encode("ascii", "ignore").decode("ascii", "replace") if name.encode("ascii", "ignore").decode("ascii", "replace") else "<MISSING>")
		store.append(address if address else "<MISSING>")
		store.append(city if city else "<MISSING>")
		store.append(state if state else "<MISSING>")
		store.append(zip if zip else "<MISSING>")
		store.append(country if country else "<MISSING>")
		store.append("<MISSING>")
		store.append(phone if phone else "<MISSING>")
		store.append(location_type if location_type else "<MISSING>" )
		store.append(lat if lat else "<MISSING>")
		store.append(lng if lng else "<MISSING>")
		store.append(hour if hour.strip() else "<MISSING>")
		store.append(page_url) 	
		return_main_object.append(store) 		
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
