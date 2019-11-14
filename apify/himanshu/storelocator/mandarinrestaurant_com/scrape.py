import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://mandarinrestaurant.com/"
    get_url ='https://mandarinrestaurant.com/locations/'
    r = requests.get(get_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")    
    main = soup.find_all('div',{'class':'wpsl-store-location'})
    for i in main:
        link =i.find('a')['href']
        location_name =i.find('a').text
        r1 = requests.get(link,headers = header)
        soup1 = BeautifulSoup(r1.text,"lxml")
        # lat = soup1.find('iframe')['src'].split('2d')[1].split('!2d')[0] 
        lat = soup1.find('iframe')['src'].split('1d')[1].split('!2d')[0].replace('11217.998304286211','45.3387268') 
        lng = soup1.find('iframe')['src'].split('1d')[1].split('!2d')[1].split('!3f')[0]
        if (len(lng)>50):
            lng = lng.split('!3d')[0] 
        # print(lng)  
        main1 = soup1.find_all('div',{'class':'et_pb_text_inner'})[1]
        st = list(main1.stripped_strings)
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(st))
        if phone_list !=[]:
            hour_tmp = soup1.find_all('div',{'class':'et_pb_text_inner'})[2]
            hour = " ".join(list(hour_tmp.stripped_strings))
            # print(hour)
            address = st[-6]
            city_tmp = st[-5].split(',')
            if (len(city_tmp)==1):
                city = city_tmp[0]
            else:
                city = city_tmp[0]
                state_tmp = city_tmp[1].replace('ON\xa0K4A 4C5',' ON K4A 4C5').strip().split(' ')
                state = state_tmp[0]
                if (len(state_tmp)==3):
                    zip = state_tmp[1]+' '+state_tmp[2]
                elif(len(state_tmp)==2):                    
                    zip = state_tmp[1]
                # print(zip)
            phone = st[-4]
            # print(city_tmp)

        else:
            main2 = soup1.find_all('div',{'class':'et_pb_text_inner'})[0]
            hour_tmp = soup1.find_all('div',{'class':'et_pb_text_inner'})[1]
            hour = " ".join(list(hour_tmp.stripped_strings))
            st1 = list(main2.stripped_strings)
            phone = st1[-4]
            address = st1[-6]
            city_tmp = st1[-5].split(',')
            city = city_tmp[0]
            state_tmp = city_tmp[1].strip().split(' ')
            state = state_tmp[0]
            zip = state_tmp[1]+ ' '+state_tmp[2]
             
      

        store=[]
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(address if address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append('CA')
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hour  if hour else '<MISSING>')
        store.append(link)
        return_main_object.append(store)
        #print("data ==== "+str(store))
    return return_main_object
        
def scrape():
    data = fetch_data()    
    write_output(data)

scrape()
