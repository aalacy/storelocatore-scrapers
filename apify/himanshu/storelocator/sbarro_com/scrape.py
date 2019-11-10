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
    locator_domain = base_url
    location_type = "<MISSING>"
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    zps=sgzip.for_radius(50)
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
                    store_number=sec['id'].split('-')[-1].strip()
                    location_name = page_url.split('/')[-1].strip()
                    city = page_url.split('/')[-2].strip().capitalize()
                    country_code = "US"
                    # try:
                    # print(main1.find('p',{'class':'location-address'}))
                    street_address= " ".join(main1.find('p',{'class':'location-address'}).text.split(',')[:-2]).strip().capitalize()
                    if "Santa Cruz" in page_url.split('/')[-3].strip():
                        state = "<MISSING>"
                    else:

                        state = page_url.split('/')[-3].strip()
                    zipp_list= main1.find('p',{'class':'location-address'}).text.split(',')[-1]
                    # print(zipp_list)
                    # ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp_list))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp_list))

                    if us_zip_list !=[]:
                        zipp=us_zip_list[0]

                    else:
                        zipp = "<MISSING>"


                    if sec.find('div',{'class':"location-phone"}) != None:
                        phone = sec.find('div',{'class':"location-phone"}).text.strip()
                    else:
                        phone = "<MISSING>"
                    # print(page_url)
                    #print(zipp)
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    latitude=sec['data-latitude']
                    longitude=sec['data-longitude']
                    if main1.find('div',{'class':"location-hours"}) != None:

                        hours_of_operation=' '.join(main1.find('div',{'class':"location-hours"}).stripped_strings).replace('Hours of Operation','').strip()
                    else:
                        hours_of_operation = "<MISSING>"
                    # print(phone)


                else:

                    # print(page_url)
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    continue
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                if str(store[1]) + str(store[2]) not in addresses:
                    addresses.append(str(store[1]) + str(store[2]))

                    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                    #print("data = " + str(store))
                    #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store
        # except:
        #     continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
