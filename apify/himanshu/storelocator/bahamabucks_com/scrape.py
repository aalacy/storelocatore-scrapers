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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"
    }
    data="status=All"
    base_url= "http://bahamabucks.com/sc/fns/locations.php"
    r = requests.post(base_url,headers=headers,data=data)
    soup= BeautifulSoup(r.text,"lxml")
  
    store_name=[]
    store_detail=[]
    phone=[]
    lat=[]
    log =[]
    hours=[]
    return_main_object=[]
    k=(soup.find_all("div",{"class":"col-md-12 col-sm-12"}))
    
    for i in k:
        tem_var=[]
        
        
        if i.find_all("div",{"id":"locations-center-icons"}) !=[]:
            lat.append(i.find_all("div",{"id":"locations-center-icons"})[0].a['href'].split("'/'")[-1].split(',')[0])
            log.append(i.find_all("div",{"id":"locations-center-icons"})[0].a['href'].split("'/'")[-1].split(',')[1].replace("'",""))

          
   

        if "HOURS" in list(i.stripped_strings):
            hourss = " ".join(list(i.stripped_strings)).replace("HOURS","")
            if hourss:
                hours.append(hourss)
                # print(hourss)
            else:
                hours.append("<MISSING>")
                # print("<MISSING>")

            # hours.append(" ".join(list(i.stripped_strings)).replace("HOURS","<MISSING>"))
        else:
            name = list(i.stripped_strings)[0]
            st = list(i.stripped_strings)[1].replace("PR","")
            city = list(i.stripped_strings)[2].split(',')[0]
            state = list(i.stripped_strings)[2].split(',')[1].split( )[0]
            zipcode = list(i.stripped_strings)[2].split(',')[1].split( )[1]

           
            if list(i.stripped_strings)[3:] !=[]:
                phone = list(i.stripped_strings)[3]
            else:
                phone ="<MISSING>"
            
            store_name.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("bahamabucks")
            store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("http://bahamabucks.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(lat[i])
        store.append(log[i])
        store.append(hours[i])
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




