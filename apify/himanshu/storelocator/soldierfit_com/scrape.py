import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://soldierfit.com/"
    return_main_object=[]
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    r = session.get(base_url+"/locations/",headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find_all('div',{"class":"soldierfit_address"})
    for dt in main:
        link=dt.find('a')['href']
        madd=list(dt.stripped_strings)
        name=madd[0]+' '+madd[1]
        address=madd[2].strip()
        ct=madd[3].replace('\xa0',' ').split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        phone=madd[-2].strip()
        r1 = session.get(base_url+link,headers=headers)
        soup1=BeautifulSoup(r1.text,'lxml')
        if "Schedule Coming Soon!" not in soup1.text:
            hour=''
            country="US"
            storeno=''
            lat=''
            lng=''
            for script in soup1.find_all('script'):
                if "var map_data" in script.text:
                    lt=json.loads(script.text.split('var map_data =')[1].split(';')[0])
                    lat=lt['locations'][0]['lat']
                    lng=lt['locations'][0]['lng']
            day=soup1.find('div',{'class':"sidebar-info"}).find_all('div',{"class":"sidebar-days"})
            hours=soup1.find('div',{'class':"sidebar-info"}).find_all('div',{"class":"sidebar-hours"})
            hour=''
            for ln in range(len(day)):
                hour+=" "+day[ln].text.strip()+' '+hours[ln].text.strip()
            storeno=''
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
            store.append("soldierfit")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour.strip() if hour.strip() else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
