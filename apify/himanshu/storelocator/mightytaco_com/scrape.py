import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url= "https://www.mightytaco.com/Locations"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    hours =[]
    phone=[]
    k=(soup.find_all("div",{'class':'address'}))
    k1=(soup.find_all("div",{'class':'hours'}))
    k2=(soup.find_all("div",{'class':'phoneRow clear'}))

    for j in k2:
        phone.append(list(j.stripped_strings)[0])
       
    for j in k1:
        hours.append(" ".join(list(j.stripped_strings)))
        
    
    for index,j in enumerate(k):
        tem_var=[]
        st =(list(j.stripped_strings)[0].split(',')[0])
        city = list(j.stripped_strings)[0].split(',')[1]
        state = list(j.stripped_strings)[0].split(',')[2].split( )[0]
        zip1 = list(j.stripped_strings)[0].split(',')[2].split( )[1]
       
        tem_var.append("https://www.mightytaco.com")
        tem_var.append(city)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone[index])
        tem_var.append("mightytaco")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours[index])
        return_main_object.append(tem_var)
   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


