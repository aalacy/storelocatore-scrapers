import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

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
    base_url= "https://www.riddlesjewelry.com/storelocator/index/loadstore/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k = (json.loads(soup.text))

    for idx, val in enumerate(k['storesjson']):
        tem_var=[]
        street_address =''
        street_address1 = val["address"].split(',')
        phone = val["phone"]
        latitude = val["latitude"]
        longitude =val["longitude"]
        zipcode = val['zipcode']
        state =val['state']
        city = val['city']
         
        store_name.append(val['store_name'])
       

        if len(street_address1)==2:
            
            street_address= (street_address1[0])
        else:
            street_address =(street_address1)[0]
        
        
        tem_var.append(street_address)
        tem_var.append(city if city else "<MISSING>" )
        tem_var.append(state if state else "<MISSING>" )
        tem_var.append(zipcode if zipcode else "<MISSING>")
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("riddlesjewelry")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append("<MISSING>")
        store_detail.append(tem_var)
      
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.riddlesjewelry.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
