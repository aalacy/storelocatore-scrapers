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
    return_main_object = []
    address1 = []
    
    r = requests.get("http://weingartenrealty.propertycapsule.com/cre/commercial-real-estate-listings/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    k  = soup.find_all('div', {'class': 'properties-3'})[1].find_all('a') 
    for i in k:
        tem_var = []
        link = i['href']

        r1 = requests.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        address_tmp1 = soup1.find('span', {'class': 'h-adr'})
        # address_tmp = list(address_tmp1.stripped_strings)
        if address_tmp1 is not None:
            address_tmp2 = soup1.find('span', {'class': 'h-adr'})
            address_tmp = list(address_tmp2.stripped_strings)
            location_name = address_tmp[0]
            address = address_tmp[1]
            city = address_tmp[2]
            state = address_tmp[4]
            zip = address_tmp[5]
            lat = address_tmp[7].split(',')[0].strip()
            lng = address_tmp[7].split(',')[1].strip()
            
        else:
            address_tmp2 = soup1.find_all('a', {'class': 'property-detail'})
            for i in address_tmp2:
                link= i['href']
                r2 = requests.get(link, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                address_tmp2 = soup2.find('span', {'class': 'h-adr'})
                address_tmp = list(address_tmp2.stripped_strings)
                lat_tmp = address_tmp[7].split(',')
                if (len(lat_tmp)==2):
                    location_name = address_tmp[0]
                    address = address_tmp[1]
                    city = address_tmp[2]
                    state = address_tmp[4]
                    zip = address_tmp[5]
                    lat = address_tmp[7].split(',')[0].strip()
                    lng = address_tmp[7].split(',')[1].strip()
                elif(len(lat_tmp)==1):
                    address_tmp = list(address_tmp2.stripped_strings)
                    location_name = address_tmp[0]
                    address = address_tmp[2]
                    city = address_tmp[3]
                    state = address_tmp[5]
                    zip = address_tmp[6]
                    lat = address_tmp[8].split(',')[0].strip()
                    lng = address_tmp[8].split(',')[1].strip()
                else:
                    address_tmp = list(address_tmp2.stripped_strings)
                    location_name = address_tmp[0]
                    address = address_tmp[1]
                    city = address_tmp[2]
                    state = address_tmp[4]
                    zip = '<MISSING>'
                    lat = address_tmp[6].split(',')[0].strip()
                    lng = address_tmp[6].split(',')[1].strip()

               
                # print(address_tmp[7])
                # print('=============================')

        tem_var.append('http://weingartenrealty.propertycapsule.com/')
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append("<MISSING>")
        tem_var.append(link)
        print(tem_var)
        return_main_object.append(tem_var)
                   
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
