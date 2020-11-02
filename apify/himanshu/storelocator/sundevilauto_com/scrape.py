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
  
    base_url= "https://www.sundevilauto.com/wp-content/uploads/json/stores.json?ver=0.5.6.1563220104"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    k= json.loads(soup.text.replace("var sda_stores = ",""))
    for i in k:
        tem_var=[]
        time = ''
        name = i['title']
        st = i['store_address_1']
        city = i['store_city']
        state = i['store_state']
        zip1 = i['store_zip']
        h1 = i['store_hours']
        lat = i['store_lat']
        log = i['store_long'] 
        store_no= i['store_number']
        phone  = i['store_phone_number']
        for  h in h1:
            time = time +h['day_of_week']+' '+h['operating_hours']
        
        tem_var.append("https://www.sundevilauto.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append(store_no)
        tem_var.append(phone)
        tem_var.append("sundevilauto")
        tem_var.append(lat)
        tem_var.append(log)
        tem_var.append(time)
        return_main_object.append(tem_var)
        
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


