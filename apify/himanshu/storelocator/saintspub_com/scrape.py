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
    
    r = session.get("https://saintspub.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup)
    main  = soup.find_all('div', {'class': 'et_pb_section et_pb_section_1 et_pb_with_background et_section_regular'})


    # print(k)
    for i in main:
        
        link1 = i.find_all('a')
        for link2 in link1:            
            link3 = link2['href']
            if 'https' in link3:
                tem_var = []
                link = link2['href']
                r1 = session.get(link, headers=headers)
                soup1 = BeautifulSoup(r1.text, "lxml")
                # print(soup)
                main2  = soup1.find('div', {'class': 'entry-content'})
                address_tmp = list(main2.stripped_strings)
                phone =re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(address_tmp))[0]
                location_name = address_tmp[0]
                address_tmp1 = address_tmp[1].split(',')
                if(len(address_tmp1)==2):
                    address_tmp2 =address_tmp1[0].split('.')
                    address = address_tmp2[0]
                    city  =address_tmp2[1]
                    state_tmp  = address_tmp1[1].strip().split(' ')
                    state = state_tmp[0]
                    zip =state_tmp[1]
                elif(len(address_tmp1)==3):
                    address = address_tmp1[0]
                    city = address_tmp1[1].strip()
                    state = address_tmp1[2].strip()
                    zip = '<MISSING>'
                hour_tmp = " ".join(address_tmp).split('HOURS')[1].split('BOOK YOUR PARTY')
                if (len(hour_tmp)==2):
                    # hour1 = " ".join(address_tmp).split('HOURS')[1].spilt('Host')
                    hour = hour_tmp[0].strip()
                else:
                    hour = hour_tmp[0].split('Host')[0].strip()
                    # print(hour)
                 
 
                  
                tem_var.append('https://saintspub.com/')
                tem_var.append(location_name)
                tem_var.append(address)
                tem_var.append(city)
                tem_var.append(state) 
                tem_var.append(zip)
                tem_var.append('US')
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hour)
                tem_var.append(link)
                return_main_object.append(tem_var)
                    
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
