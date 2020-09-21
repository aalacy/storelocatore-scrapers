import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    body ='{"lat":21.1597606,"lng":72.79591219999998,"top":154,"findAStore":true}'
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    "Content-Type": "application/json; charset=UTF-8"
    }
    base_url= "https://www.searsauto.com/find-a-store?q=395007"

   
    r = requests.post(base_url,headers=headers,data=body)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k = (json.loads(soup.text))

    for idx, val in enumerate(k['results']):
        tem_var=[]
        # print(val['detailsUrl'])
        # exit()
        street_address = val["address1"]
        storeNumber = val["storeNumber"]
        city = val['city']
        state =val["state"]
        zipcode = val["postalCode"]
        phone = val['phone']
        latitude =val['latitude']
        longitude =val['longitude']
        hours =val['hours']
        time =''
        for j in hours:
            
            if "open" in j:
                time = time+ ' '+ j["dayOfWeek"]+' '+ j['open'] +'-'+ j["close"]
        
        if "Hanover Mal/1775 Washingt" in street_address:
            tem_var.append("1775 Hanover Mal Washingt")
        else:
            tem_var.append(street_address.replace("Raceway Ml/","").replace("/Willow Gr Mall",""))

        store_name.append(city)
        tem_var.append(city if city else "<MISSING>" )
        tem_var.append(state if state else "<MISSING>" )
        tem_var.append(zipcode if zipcode else "<MISSING>")
        tem_var.append("US")
        tem_var.append(storeNumber)
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(time)
        tem_var.append("https://www.searsauto.com"+val['detailsUrl'])
        store_detail.append(tem_var)
      
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.searsauto.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        # store.append()
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


