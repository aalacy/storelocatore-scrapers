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
    store_name = []
    lat = []
    lng=[]
    return_main_object = []
    address1 = []
    phone = []
    get_url= 'http://deweyspizza.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?t=1571049679253' 
    domain_url = 'https://www.omnisourceusa.com/'
    # tem_var=[]
    hour2 = []
   
    address_s =[]
    r = requests.get(get_url, headers=headers)
    # print(r)
    soup = BeautifulSoup(r.text,'lxml')
    location1 = soup.find_all('location')
    address1 = soup.find_all('address')   
    latitude1 = soup.find_all('latitude')
    longitude1 = soup.find_all('longitude')
    hour = soup.find_all('operatinghours')
    telephone1 = soup.find_all('telephone')
    storeId1 = soup.find_all('storeid')
    for i in hour:
        
        hour1= BeautifulSoup(i.text,'lxml')
        time = list(hour1.stripped_strings)
        if time[-1]=="Party Room Available":
            del time[-1]
        # print(" ".join(time))
        hour2.append(" ".join(time))
        # hour.append(list(hour1.stripped_strings)[0]+ ' '+list(hour1.stripped_strings)[1]+ ' '+list(hour1.stripped_strings)[2])
        
    # print(hour2)
    for i in location1:
        store_name.append(i.text)
        
    
    for i in address1:
        tem_var =[]
        address2= i.text.split(',')
        if(len(address2)==2):
            address3= address2[0].split('.')
            state_tmp = address2[1].strip().split(' ')
            state =state_tmp[0]
            zip = state_tmp[1]
            if(len(address3)==1):
                address = ' ' .join(address3[0].split(' ')[:-1])
                city = address3[0].split(' ')[-1].replace('O&#39;','').replace('Park','Overland Park')
            elif(len(address3)==3):
                city1 = address2[0].split('.')[-1]
                address = ' ' .join(address2[0].split('.')[:-1]).replace('Cleveland Hts','')
                if(city1!=''):
                    city = address2[0].split('.')[-1].strip()
                else:
                    city =address2[0].split('.')[1].strip()
            elif(len(address3)==2):  
                address =address3[0].strip()
                city = address3[1].replace('Suite D','').strip()
        elif(len(address2)==1):
            address3= ' ' .join(address2[0].strip().split(' ')[:-2])   
            city=  address2[0].strip().split(' ')[-2]
            zip = address2[0].strip().split(' ')[-1] 
            state= '<MISSING>'

        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        store_detail.append(tem_var)
        
          
    for i in telephone1:
        phone.append(i.text)
         
    for i in latitude1:
        lat.append(i.text.strip())

    for i in longitude1:
        lng.append(i.text.strip())


  
    for i in range(len(store_name)):
       store = list()
       store.append("http://deweyspizza.com")
       store.append(store_name[i])
       store.extend(store_detail[i])
       store.append(phone[i])
       store.append("<MISSING>")
       store.append(lat[i])
       store.append(lng[i])
       store.append(hour2[i])
       store.append("<MISSING>")
       #print(store)
       if store[2] in address_s:
            continue
        
       address_s.append(store[2])
       return_main_object.append(store)

        
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
