import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    store_detail = []
    
    lat = []
    lng=[]
    return_main_object = []
    address1 = []
    tmp_url= 'https://www.firstlightfcu.org'
    get_url= 'https://www.firstlightfcu.org/branches' 
    
    # tem_var=[]
 
   
    
    r = requests.get(get_url, headers=headers)
    # print(r)
    soup = BeautifulSoup(r.text,'lxml')
    # print(soup)         
  
    main =soup.find_all('span', {'class': 'name'})
    for i in main:
        tem_var = []
        link = tmp_url+i.a['href']
        r1 = requests.get(link, headers=headers)
         # print(r)
        soup1 = BeautifulSoup(r1.text,'lxml')
        location_name =soup1.find('div', {'class': 'h2'}).text
        address =soup1.find('span', {'class': 'address'}).text
        city_tmp =soup1.find('span', {'class': 'city_state_zip'}).text.split(',')
        city =city_tmp[0]
        state = city_tmp[1].split(' ')[1]
        zip = city_tmp[1].split(' ')[2]
        hour1 =soup1.find('span', {'class': 'hours'})
        hour = " ".join(list(hour1.stripped_strings))
        phone =soup1.find('span', {'class': 'phone'}).text.replace('Phone:','').strip()
        lat_tmp = soup1.find_all('script', {'type': 'text/javascript'})[7].text.split('LatLng(')[1].split('),')[0].split(',')
        lat = lat_tmp[0]
        lng = lat_tmp[1]
       
        
       
        
  

        tem_var.append(tmp_url)
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append(hour)
        tem_var.append(link)

        return_main_object.append(tem_var)
        
           
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
