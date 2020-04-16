import csv
import requests
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
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
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    returnres=[]
    base_url="https://www.steward.org/"
    r=session.get("https://locations.steward.org/index.html",headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    main=soup.find('ul',{"class":"c-directory-list-content"}).find_all('li',{'class':'c-directory-list-content-item'})
    for ltag  in main:
        if ltag.find('span',{'class':"c-directory-list-content-item-count"}).text.strip()=="(1)":
            page_url="https://locations.steward.org/"+ltag.find('a')['href'].replace('../','')
            r1=session.get(page_url,headers=headers)
            soup1= BeautifulSoup(r1.text,"lxml")
            location_name=soup1.find('h1',{"itemprop":"name","class":"Hero-midSection--name"}).text.strip()
            addr=list(soup1.find('a',{"itemprop":"address"}).stripped_strings)
            street_address=addr[0].split('Suite')[0].strip()
            ct=addr[1].strip().split(' ')
            zipp=ct[-1]
            del ct[-1]
            state=ct[-1]
            del ct[-1]
            city=' '.join(ct).strip()
            try:
                phone=soup1.find('span',{"itemprop":"telephone"}).text.strip()
            except:
                phone=""
            try:            
                latitude=soup1.find('meta',{"itemprop":"latitude"})['content'].strip()
            except:
                latitude=""
            try:
                longitude=soup1.find('meta',{"itemprop":"longitude"})['content'].strip()
            except:
                longitude=""
            try:    
                hr=soup1.find('table',{"class":"c-location-hours-details"}).find('tbody').find_all('tr',{'class':"c-location-hours-details-row"})
                hour=""
                for h in hr:
                    hour=hour+" "+h.find('td',{"class":"c-location-hours-details-row-day"}).text.strip()
                    hour=hour+" "+' '.join(list(h.find('td',{"class":"c-location-hours-details-row-intervals"}).stripped_strings))
            except:
                hour=""
            store =[]
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hour)
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store 
        else:
            link="https://locations.steward.org/"+ltag.find('a')['href']
            r1=session.get(link,headers=headers)
            soup1= BeautifulSoup(r1.text,"lxml")
            flag=True;
            try:
                main1=soup1.find('ul',{"class":"c-directory-list-content"}).find_all('li',{'class':'c-directory-list-content-item'})
            except:
                flag=False
            if flag==True:
                for ltag in main1:
                    #print(ltag.find('a')['href'])
                    if ltag.find('span',{'class':"c-directory-list-content-item-count"}).text.strip()=="(1)":
                        page_url="https://locations.steward.org/"+ltag.find('a')['href'].replace('../','')
                       # print(page_url)
                        r1=session.get(page_url,headers=headers)
                        soup1= BeautifulSoup(r1.text,"lxml")
                        location_name=soup1.find('h1',{"itemprop":"name","class":"Hero-midSection--name"}).text.strip()
                        addr=list(soup1.find('a',{"itemprop":"address"}).stripped_strings)
                        street_address=addr[0].split('Suite')[0].strip()
                        ct=addr[1].strip().split(' ')
                        zipp=ct[-1]
                        del ct[-1]
                        state=ct[-1]
                        del ct[-1]
                        city=' '.join(ct).strip()
                        try:
                            phone=soup1.find('span',{"itemprop":"telephone"}).text.strip()
                        except:
                            phone=""
                        try:            
                            latitude=soup1.find('meta',{"itemprop":"latitude"})['content'].strip()
                        except:
                            latitude=""
                        try:
                            longitude=soup1.find('meta',{"itemprop":"longitude"})['content'].strip()
                        except:
                            longitude=""
                        try:    
                            hr=soup1.find('table',{"class":"c-location-hours-details"}).find('tbody').find_all('tr',{'class':"c-location-hours-details-row"})
                            hour=""
                            for h in hr:
                                hour=hour+" "+h.find('td',{"class":"c-location-hours-details-row-day"}).text.strip()
                                hour=hour+" "+' '.join(list(h.find('td',{"class":"c-location-hours-details-row-intervals"}).stripped_strings))
                        except:
                            hour=""
                        store =[]
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zipp if zipp else "<MISSING>")
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(phone)
                        store.append("<MISSING>")
                        store.append(latitude if latitude else "<MISSING>")
                        store.append(longitude if longitude else "<MISSING>")
                        store.append(hour)
                        store.append(page_url)
                        if store[2] in addressess:
                            continue
                        addressess.append(store[2])
                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                        yield store 
                    else:
                        link="https://locations.steward.org/"+ltag.find('a')['href']
                        r1=session.get(link,headers=headers)
                        soup1= BeautifulSoup(r1.text,"lxml")
                        main2=soup1.find_all('a',{"class":"viewpractice"})
                        for atag in main2:
                            page_url="https://locations.steward.org/"+atag['href'].replace('../','')
                            #print(page_url)
                            r1=session.get(page_url,headers=headers)
                            soup1= BeautifulSoup(r1.text,"lxml")
                            location_name=soup1.find('h1',{"itemprop":"name","class":"Hero-midSection--name"}).text.strip()
                            addr=list(soup1.find('a',{"itemprop":"address"}).stripped_strings)
                            street_address=addr[0].split('Suite')[0].strip()
                            ct=addr[1].strip().split(' ')
                            zipp=ct[-1]
                            del ct[-1]
                            state=ct[-1]
                            del ct[-1]
                            city=' '.join(ct).strip()
                            try:
                                phone=soup1.find('span',{"itemprop":"telephone"}).text.strip()
                            except:
                                phone=""
                            try:            
                                latitude=soup1.find('meta',{"itemprop":"latitude"})['content'].strip()
                            except:
                                latitude=""
                            try:
                                longitude=soup1.find('meta',{"itemprop":"longitude"})['content'].strip()
                            except:
                                longitude=""
                            try:    
                                hr=soup1.find('table',{"class":"c-location-hours-details"}).find('tbody').find_all('tr',{'class':"c-location-hours-details-row"})
                                hour=""
                                for h in hr:
                                    hour=hour+" "+h.find('td',{"class":"c-location-hours-details-row-day"}).text.strip()
                                    hour=hour+" "+' '.join(list(h.find('td',{"class":"c-location-hours-details-row-intervals"}).stripped_strings))
                            except:
                                hour=""
                            store =[]
                            store.append(base_url)
                            store.append(location_name)
                            store.append(street_address)
                            store.append(city)
                            store.append(state)
                            store.append(zipp if zipp else "<MISSING>")
                            store.append("US")
                            store.append("<MISSING>")
                            store.append(phone)
                            store.append("<MISSING>")
                            store.append(latitude if latitude else "<MISSING>")
                            store.append(longitude if longitude else "<MISSING>")
                            store.append(hour)
                            store.append(page_url)
                            if store[2] in addressess:
                                continue
                            addressess.append(store[2])
                            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                            yield store 
            else:
                main2=soup1.find_all('a',{"class":"viewpractice"})
                for atag in main2:
                    page_url="https://locations.steward.org/"+atag['href'].replace('../','')
                    #print(page_url)
                    r1=session.get(page_url,headers=headers)
                    soup1= BeautifulSoup(r1.text,"lxml")
                    location_name=soup1.find('h1',{"itemprop":"name","class":"Hero-midSection--name"}).text.strip()
                    addr=list(soup1.find('a',{"itemprop":"address"}).stripped_strings)
                    street_address=addr[0].split('Suite')[0].strip()
                    ct=addr[1].strip().split(' ')
                    zipp=ct[-1]
                    del ct[-1]
                    state=ct[-1]
                    del ct[-1]
                    city=' '.join(ct).strip()
                    try:
                        phone=soup1.find('span',{"itemprop":"telephone"}).text.strip()
                    except:
                        phone=""
                    try:            
                        latitude=soup1.find('meta',{"itemprop":"latitude"})['content'].strip()
                    except:
                        latitude=""
                    try:
                        longitude=soup1.find('meta',{"itemprop":"longitude"})['content'].strip()
                    except:
                        longitude=""
                    try:    
                        hr=soup1.find('table',{"class":"c-location-hours-details"}).find('tbody').find_all('tr',{'class':"c-location-hours-details-row"})
                        hour=""
                        for h in hr:
                            hour=hour+" "+h.find('td',{"class":"c-location-hours-details-row-day"}).text.strip()
                            hour=hour+" "+' '.join(list(h.find('td',{"class":"c-location-hours-details-row-intervals"}).stripped_strings))
                    except:
                        hour=""
                    store =[]
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp if zipp else "<MISSING>")
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(longitude if longitude else "<MISSING>")
                    store.append(hour if hour else "<MISSING>")
                    store.append(page_url)
                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    yield store 
       
def scrape():
    data = fetch_data();
    write_output(data)
scrape()
