import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    # zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    

    locator_domain = 'https://beallsoutlet.com/'
    r = session.get('https://stores.beallsoutlet.com/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    main = soup.find('div',{'class':'no-results'}).find_all('div',{'class':'map-list-item is-single'})
    for i in main:
        link= i.find('a')['href']
        r1 = session.get(link,headers = headers)
        soup1 = BeautifulSoup(r1.text,'lxml')
        main2 = soup1.find_all('div',{'class':'map-list-item-wrap is-single'})
        for i in main2:
            link1= i.find('a')['href']
            r2 = session.get(link1,headers = headers)
            soup2 = BeautifulSoup(r2.text,'lxml')
            main3 = soup2.find('div',{'class':'address'})
            lat_tmp = soup2.find('div',{'class':'directions'}).find('a')['href'].split('location&daddr=')[1]
            location_name_tmp = soup2.find('h3',{'class':'location-name'})
            location_name = list(location_name_tmp.stripped_strings)[0]
            phone = soup2.find('div',{'class':'phone'}).text.strip()
            country_code = 'US'

            lat = lat_tmp.split(',')[0]
            lng = lat_tmp.split(',')[1]
            

            st = list(main3.stripped_strings)
            if (len(st)== 2):

                address = st[0]
                city = st[1].split(',')[0]          # 
                state = st[1].split(',')[1].split(' ')[1]
                zip = st[1].split(',')[1].split(' ')[2]
                # print(zip)
                
            elif (len(st)== 3):
                address = st[0]
                city = st[2].split(',')[0]
                state = st[2].split(',')[1].split(' ')[1]
                zip = st[2].split(',')[1].split(' ')[2]  

            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(address if address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip if zip else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append( '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append('<MISSING>')
            store.append(lat if lat else '<MISSING>')
            store.append(lng if lng else '<MISSING>')
            store.append('<MISSING>')
            store.append(link1)          
            return_main_object.append(store)     
            yield store
            # exit()





    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
# map-list-item-wrap is-single
