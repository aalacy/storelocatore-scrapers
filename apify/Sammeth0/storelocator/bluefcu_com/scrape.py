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
		print(address)
		city=cities.h4.text.split('\n')[1].split(',')[0].strip()
		state=cities.h4.text.split('\n')[1].split(',')[1].strip()
		zip=cities.h4.text.split('\n')[1].split(',')[2].strip()
		storeno=cities.h4.text.split('\n')[0].strip().split(' ')[0]
		num=cities.h4.text.split('\n')[0].strip().split(' ')[1].split(' ')[0]
		if len(num)==1:
			storeno=storeno+num
		print(storeno)
		phone=cities.p.contents[0]
		atms=div.find(class_="branch-location__24-hr-services")
		yes_atm=atms.find(class_='fa fa-check-circle')
		location_type_atm=atms.text.strip()
		if (yes_atm!=''):
			atm=0
			if location_type_atm.find('ATM')!=-1 :
				atm=1
		branchs=soup.find(class_="branch-location__special-services")
		yes_branch=branchs.find(class_='fa fa-check-circle')
		location_type_branch=branchs.text.strip()
		if (yes_branch!=''):
			branch=0
			if location_type_branch.find('Branch')!=-1 :
				branch=1
		if ((atm ==1) and (branch ==1)):
			location_type='ATM|Branch'
		elif atm==1:
			location_type='ATM'
		elif branch==1:
			location_type='Branch'
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
		store.append(name if name else "<MISSING>")
		store.append(address if address else "<MISSING>")
		store.append(city if city else "<MISSING>")
		store.append(state if state else "<MISSING>")
		store.append(zip if zip else "<MISSING>")
		store.append(country if country else "<MISSING>")
		store.append(storeno if storeno else "<MISSING>")
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
