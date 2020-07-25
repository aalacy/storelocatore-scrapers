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
    
    lat = []
    lng=[]
    return_main_object = []
    address1 = []
    base_url ='https://www.orderjoes.com/wp-content/themes/understrap-child/locations_data.php'
    domain_url = 'https://www.orderjoes.com/'
    

    r = session.get(
    base_url, headers=headers).json()
    k = session.get('https://www.orderjoes.com/locations/', headers=headers)
    soup1 = BeautifulSoup(k.text, "lxml")
    main =soup1.find('ul', {'id': 'list'}).find_all('a')

    for i in main:
        lat.append(i.attrs['data-lat'])
        lng.append(i.attrs['data-lng'])
    
    for index,i in enumerate(r,start=0):
        tem_var =[]
        obj= r[i]
        location_name = obj['name']
        address =obj['street']
        city_tmp = obj['address'].split(',')
        city =city_tmp[0]
        state_tmp = city_tmp[1].split(' ')
        state= state_tmp[1]
        phone= obj['phone'].replace('JOES','')
        if city == 'Brighton':
            zip = city_tmp[2]
        else:
            zip = state_tmp[2]
        hour1=BeautifulSoup( obj['hours'], "lxml" )
        hour =" ".join(list(hour1.stripped_strings)).replace('Online Ordering is not yet available at this location. Please call to place your order. Thank you!','')
        
        tem_var.append(domain_url)
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lat[index])
        tem_var.append(lng[index])
        tem_var.append(hour)
        tem_var.append('https://www.orderjoes.com/locations/') 
        # print(tem_var)

        return_main_object.append(tem_var)
        
           
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
