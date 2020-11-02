import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://trufusion.com/"
    return_main_object = []
    r = session.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{'class':'studio-area'}).find('div',{'class':'studio-wrap'}).find_all('a')
    for atag in main:
        country="US"
        hour=''
        zip=''
        phone=''
        lat=''
        lng=''
        page_url = base_url+atag['href'].replace(" ","%20")
        r1 = session.get(page_url)
        soup1=BeautifulSoup(r1.text,'lxml')
        if "studioName" in atag['href']:
            name=soup1.find('h2',{"itemprop":"name"}).text.strip()
            address=soup1.find('span',{"itemprop":"streetAddress"}).text.strip()
            ct=soup1.find('span',{"itemprop":"addressLocality"}).text.strip().split(',')
            if len(ct)==2:
                city=ct[0].strip()
                state=ct[1].strip()
            else:
                city=ct[0].strip()
            if soup1.find('div',{"class":'operation-hour'})!=None:
                hour=' '.join(list(soup1.find('div',{"class":'operation-hour'}).find('ul').stripped_strings)).strip()
            if soup1.find('span',{"itemprop":"postalCode"})!=None:
                zip=soup1.find('span',{"itemprop":"postalCode"}).text.strip()
            if soup1.find('a',{"itemprop":"telephone"})!=None:
                phone=soup1.find('a',{"itemprop":"telephone"}).text.strip()
        else:
            main1=soup1.find('div',{"id":'main'}).find('div',{"class":"one"})
            try:
                name=main1.find_all('p')[1].text.strip()
                address=main1.find_all('p')[2].text.strip()
                madd=main1.find_all('p')[3].text.strip().split(',')
                city=madd[0].strip()
                state=madd[1].strip().split(' ')[0].strip()
                zip=madd[1].strip().split(' ')[1].strip()
            except IndexError:
                name=main1.find_all('p')[0].text.strip()
                address=main1.find_all('p')[1].text.strip()
                madd=main1.find_all('p')[2].text.strip().split(',')
                city=madd[0].strip()
                state=madd[1].strip().split(' ')[0].strip()
                zip=madd[1].strip().split(' ')[1].strip()
        if city=="Bellevue":
            state = "WA"
        if "WE'RE COMING FOR YOU" in soup1.find('div',{'class':'inner2'}).text:
            location_type = "coming soon"
        else:
            location_type = "<MISSING>"
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type)
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        return_main_object.append(store)                
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()