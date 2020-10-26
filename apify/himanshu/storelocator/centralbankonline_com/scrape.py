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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

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
    "https://www.centralbankonline.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    
    address_tmp = soup.find_all('div', {'class': 'location-row'})
    for i in address_tmp:
        tem_var =[]
        location_name = i.find('h3', {'class': 'location-name'}).text
        address_tmp2 = i.find_all('div', {'class': 'threecol'})[1].find('p')
        hour = i.find_all('div', {'class': 'threecol'})[2].text.replace('\r','').replace('\n','')
        print(hour)
        address = list(address_tmp2.stripped_strings)[0]
        city_tmp = list(address_tmp2.stripped_strings)[1].split(',')
        city = city_tmp[0]
        state_tmp = city_tmp[1].split(' ')
        state = state_tmp[1]
        zip1 = state_tmp[2]
        phone  = list(address_tmp2.stripped_strings)[2].replace('Phone: ','')
        
       
                   
        tem_var.append('https://www.centralbankonline.com/')
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip1)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("centralbankonline")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hour)
        return_main_object.append(tem_var)
                   
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
