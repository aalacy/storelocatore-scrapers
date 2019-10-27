import bs4 as bs
import urllib.request
from bs4 import BeautifulSoup
from lxml import html
import csv
import pandas as pd



locator_domain='centurynationalbank_com'
page_url='https://centurynationalbank.com/locations/'
country_code='US'
latitude='MISSING'
longitude='MISSING'


csv_file = open('data2.csv', 'w', encoding='utf-8')
fieldnames=['locator_domain','page_url','location_name','street_address','city','state','zip','country_code','store_number','phone','location_type','latitude','longitude','hours_of_operation','page_url']
csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, escapechar='"',lineterminator = '\n')
csv_writer.writeheader()


source = urllib.request.urlopen(page_url).read()
soup = bs.BeautifulSoup(source,'lxml')

stores=soup.findAll(class_="medium-6 columns")
for store in stores:
	try:
		location_names=store.findAll(class_="sub-head fw-light")
		for name in location_names:
			location_name=name.a.text
	except:
		location_name='MISSING'
		
	street_addresses=store.findAll(class_="branch-address fw-light")
	for address in street_addresses:
		try:
			street_address=' '.join(address.contents[0].split(' ')[1::]).replace(',',' ').replace('\n','')
		except:
			street_address='MISSING'
		try:
			city=address.contents[2].split(',')[0].replace(',',' ').replace('\n','')
		except:
			city='MISSING'
		try:
			state=address.contents[2].split(',')[1].strip().split(' ')[0].replace(',',' ').replace('\n','')
		except:
			state='MISSING'
		try:
			zip=address.contents[2].split(',')[1].strip().split(' ')[1].replace(',',' ').replace('\n','')
		except:
			zip='MISSING'
		try:
			phone=address.get_text().split()[5].replace(',',' ').replace('\n','')
		except:
			phone='MISSING'
		try:
			store_number=address.contents[0].split(' ')[0].strip().replace(',',' ').replace('\n','')
		except:
			store_number='MISSING'
			
		hours=store.findAll(class_="large-6 small-6 columns")
		for hour in hours:
			try:
				hours_of_operation=hour.text.replace(',',' ').replace('\n','')
			except:
				hours_of_operation='MISSING'
				
		location_types=store.findAll(class_='large-4 columns')
		for type in location_types:
			try:
				location_type=type.text.replace(',',' ').replace('\n','')
			except:
				location_type='MISSING'
		
		data={'locator_domain':locator_domain,'page_url':page_url,'location_name':location_name,'street_address':street_address,'city':city,'state':state,'zip':zip,'country_code':country_code,'store_number':store_number,'phone':phone,'location_type':location_type,'latitude':latitude,'longitude':longitude,'hours_of_operation':hours_of_operation,'page_url':page_url}
		csv_writer.writerow(data)
	
csv_file.close()
