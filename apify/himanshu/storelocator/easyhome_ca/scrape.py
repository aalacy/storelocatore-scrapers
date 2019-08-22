import csv
import requests
from bs4 import BeautifulSoup
import re
import json
​
​
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
​
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
​
​
def fetch_data():
  
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://easyhome.ca/store/all"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
  
    name_store=[]
    store_detail=[]
    
    return_main_object=[]
   
    k=json.loads(soup.text,strict=False)
    for index,i in enumerate(k):
        tem_var=[]
        st = i['address1']
        country = "CA"
        lat = i['latitude']
        log =i['longitude']
        postal =i['zip']
        name = i['storeName']
        storeCode = i['storeCode']
        state =i['state'].split('-')[0]
        city =i['city']
        phone =i["phone"]
        if "saturdayClose" in i or "saturdayOpen" in i:
            time =str(i['saturdayOpen'])+ ' '+str(i['saturdayClose'])+ ' '+str(i["weekdayOpen"])+' ' + str(i['weekdayClose'])
        
        else:
            time="<MISSING>"
            
​
       
​
       
 
​
        tem_var.append("https://easyhome.ca")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(postal)
        tem_var.append("CA")
        tem_var.append(storeCode)
        tem_var.append(phone)
        tem_var.append("easyhome")
        tem_var.append(lat)
        tem_var.append(log)
        tem_var.append(time)
        return_main_object.append(tem_var)
​
    return return_main_object
​
​
def scrape():
    data = fetch_data()
    write_output(data)
​
​
scrape()
