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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    store_detail = []
    store_name = []
    return_main_object = []
    address1 = []
    
    r = session.get(
    "https://hobees.com", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    
   
    
    k  = soup.find_all('li', {'id': 'menu-item-44'})
    for i in k:
        
        li = i.find_all('li')
        
        for i in li:
            tem_var = []
            link = i.find('a')['href']
            r1 = session.get( link, headers=headers) 
            soup1 = BeautifulSoup(r1.text, "lxml")
            location_name = soup1.find('h1', {'class': 'main-title'}).text
            
          
            address_tmp = soup1.find_all('div', {'class': 'avia_textblock'})[1]
            # print(address_tmp.text)
            address = list(address_tmp.stripped_strings)[0]
            city_tmp = list(address_tmp.stripped_strings)[1].split(',')
            city = city_tmp[0]
            state_tmp = city_tmp[1].split(' ')
            state= state_tmp[1]
            zip1= state_tmp[2]
            phone = list(address_tmp.stripped_strings)[2]
            lati_tmp =soup1.find_all('div', {'class': 'avia_textblock'})[0].iframe['src'].split('&sspn=0.')
            lati_tmp1= lati_tmp[0].split('&sll=')
            lati_tmp2 = lati_tmp1[1].split(',')
            latitude = lati_tmp2[0]
            longitude = lati_tmp2[1]
            hour_tmp= soup1.find_all('div', {'class': 'avia_textblock'})[2]
            hour_tmp1 = hour_tmp.find_all('p')
            hour = hour_tmp1[3].text.replace("Birthday: October 1986","Monday – Friday: 7:00 a.m. – 8:30 p.m.Saturday – Sunday: 7:30 a.m. – 8:30 p.m.")
          
       
                   
            tem_var.append('https://hobees.com')
            tem_var.append(location_name)
            tem_var.append(address)
            tem_var.append(city)
            tem_var.append(state) 
            tem_var.append(zip1)
            tem_var.append('US')
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hour.replace("\n","").replace("Hours of Operation:",""))
            tem_var.append(link)
            #print(tem_var)
            return_main_object.append(tem_var)
                   
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
