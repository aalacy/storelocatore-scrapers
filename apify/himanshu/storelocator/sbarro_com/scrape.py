import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://sbarro.com"
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    zps=sgzip.for_radius(50)
    return_main_object = []
    output=[]
    for zp in zps:
        try:
            r = requests.get(base_url+"/locations/?user_search="+zp,headers=headers)
            soup=BeautifulSoup(r.text,'lxml')
            if soup.find('div',{"id":"locations-search-form-results"})!=None:
                main=soup.find('div',{"id":"locations-search-form-results"}).find_all('section',{'class':"locations-result"})
                for sec in main:
                    link=sec.find('a')['href']
                    r1=requests.get(base_url+link)
                    soup1=BeautifulSoup(r1.text,'lxml')
                    main1=soup1.find('div',{'id':'location-content-details'})
                    storeno=sec['id'].split('-')[-1].strip()
                    name=main1.find('h1',{'class':'location-name'}).text.strip()
                    adr=main1.find('p',{'class':'location-address'}).text.strip().split(',')
                    address=adr[0].strip()
                    country="US"
                    city=adr[1].strip()
                    st=adr[2].strip().split(' ')
                    state=st[0].strip()
                    zip=''
                    if len(st)>1:
                        zip=st[1].strip()
                    phone=''
                    if sec.find('div',{'class':"location-phone"})!=None:
                        phone=sec.find('div',{'class':"location-phone"}).text.replace('\n','')
                        phone=re.sub(r'\n+','',phone)
                    lat=sec['data-latitude']
                    lng=sec['data-longitude']
                    hour=' '.join(main1.find('div',{'class':"location-hours"}).stripped_strings)
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
                    store.append("pumpitupparty")
                    store.append(lat if lat else "<MISSING>")
                    store.append(lng if lng else "<MISSING>")
                    store.append(hour if hour else "<MISSING>")
                    adrr=address+' '+city+' '+state+' '+zip
                    if adrr not in output:
                        output.append(adrr)
                        return_main_object.append(store)
        except:
            continue            
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
