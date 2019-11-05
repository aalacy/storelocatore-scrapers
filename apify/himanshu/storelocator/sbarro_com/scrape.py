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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://sbarro.com"
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    zps=sgzip.for_radius(100)
    return_main_object = []
    addresses = []
    for zp in zps:
        # try:
        r = requests.get(base_url+"/locations/?user_search="+zp,headers=headers)
        soup=BeautifulSoup(r.text,'lxml')
        if soup.find('div',{"id":"locations-search-form-results"})!=None:
            main=soup.find('div',{"id":"locations-search-form-results"}).find_all('section',{'class':"locations-result"})
            for sec in main:
                link=sec.find('a')['href']
                r1=requests.get(base_url+link)
                soup1=BeautifulSoup(r1.text,'lxml')
                page_url = base_url+link
                main1=soup1.find('div',{'id':'location-content-details'})
                if main1 != None:
                    storeno=sec['id'].split('-')[-1].strip()
                    name = page_url.split('/')[-1].strip()
                    city = page_url.split('/')[-2].strip().capitalize()
                    country = "US"
                    # try:
                    # print(main1.find('p',{'class':'location-address'}))
                    address= " ".join(main1.find('p',{'class':'location-address'}).text.split(',')[:-2]).strip().capitalize()
                    state = page_url.split('/')[-3].strip()
                    zipp_list= main1.find('p',{'class':'location-address'}).text.split(',')[-1]
                    # print(zipp_list)
                    # ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp_list))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp_list))

                    if us_zip_list !=[]:
                        zip=us_zip_list[0]

                    else:
                        zip = "<MISSING>"


                    if sec.find('div',{'class':"location-phone"}) != None:
                        phone = sec.find('div',{'class':"location-phone"}).text.strip()
                    else:
                        phone = "<MISSING>"
                    print(zip,phone)
                    lat=sec['data-latitude']
                    lng=sec['data-longitude']
                    if main1.find('div',{'class':"location-hours"}) != None:

                        hour=' '.join(main1.find('div',{'class':"location-hours"}).stripped_strings).replace('Hours of Operation','').strip()
                    else:
                        hour = "<MISSING>"
                    # print(phone)


                else:

                    # print(page_url)
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    continue

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
                store.append(page_url if page_url else "<MISSING>")

                if storeno in addresses:
                    addresses.append(storeno)
                # print("data == "+str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~')
                return_main_object.append(store)
        # except:
        #     continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
