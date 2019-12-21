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


    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    base_url = "https://sbarro.com"
    locator_domain = base_url
    location_type = "<MISSING>"
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    return_main_object = []
    addresses = []
    while zip_code:
        #print("---------------------------------",zip_code)
        result_coords = []
        r = requests.get(base_url+"/locations/?user_search="+zip_code,headers=headers)
        soup=BeautifulSoup(r.text,'lxml')
        if soup.find('div',{"id":"locations-search-form-results"})!=None:
            main=soup.find('div',{"id":"locations-search-form-results"}).find_all('section',{'class':"locations-result"})
            current_results_len = len(soup.find('div',{"id":"locations-search-form-results"}).find_all('section',{'class':"locations-result"}))

            for sec in main:
                link=sec.find('a')['href']
                r1=requests.get(base_url+link)
                soup1=BeautifulSoup(r1.text,'lxml')
                page_url = base_url+link
                main1=soup1.find('div',{'id':'location-content-details'})
                # print('----------------------------------')
                if main1 != None:
                    add = main1.find('p',{'class':'location-address'}).text.strip()
                    # phone = soup1.find("span",{"class":"btn-label"}).text.strip()
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(soup1.find("span",{"class":"btn-label"}).text.strip()))
                    if phone_list:
                        phone =  phone_list[-1]

                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(add))
                    if us_zip_list:
                        zipp = us_zip_list[-1]
                        country_code = "US"
                    street_address = " ".join(add.split(",")[:-2]).capitalize()
                    city = add.split(",")[-2].capitalize()
                    state_list = re.findall(r' ([A-Z]{2})', str(add.split(",")[-1]))
                    if state_list:
                        state = state_list[-1]
                    # store_number=sec['id'].split('-')[-1].strip()
                    latitude=sec['data-latitude']
                    longitude=sec['data-longitude']
                    result_coords.append((latitude, longitude))
                    # print(longitude)
                    location_name = main1.find("h1",{"class":"location-name"}).text.strip()
                    try:
                        hours_of_operation = (" ".join(list(main1.find("div",{"class":"location-hours"}).stripped_strings)))
                    except:
                        hours_of_operation = "<MISSING>"
                    store_number = "<MISSING>"
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    if str(store[1]) + str(store[2]) not in addresses:
                        addresses.append(str(store[1]) + str(store[2]))
                        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                        #print("data = " + str(store))
                        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        yield store

        if current_results_len < MAX_RESULTS:
           # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
           # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


                
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
