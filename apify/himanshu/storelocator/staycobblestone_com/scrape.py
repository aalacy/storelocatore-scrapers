import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    data ="action=get_properties_for_map"
    base_url= "https://www.staycobblestone.com/wp-admin/admin-ajax.php"
    r = session.post(base_url,data=data,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object=[]
    k = json.loads(soup.text)
    for k1 in k:
        for val in k[k1]['properties']:
            tem_var=[]
            zipcode =''
            address = (k[k1]['properties'][val]['address'])
            city = k[k1]['properties'][val]['city']
            state = k[k1]['properties'][val]['state']
            phone =k[k1]['properties'][val]['phone']
            types =k[k1]['properties'][val]['type'] 
            page_url = k[k1]['properties'][val]['link']
            zipcode1 = k[k1]['properties'][val]['address_full'].split( )[-1]
            if zipcode1.isdigit():
                zipcode = zipcode1
            else:
                zipcode ="<MISSING>"
            latitude = k[k1]['properties'][val]['latitude']
            longitude = k[k1]['properties'][val]['longitude']
            location_name = str(city)+", "+str(state)
            tem_var.append("https://www.staycobblestone.com")
            tem_var.append(location_name if location_name else "<MISSING>" )
            tem_var.append(address if address else "<MISSING>" )
            tem_var.append(city if city else "<MISSING>" )
            tem_var.append(state if state else "<MISSING>" )
            tem_var.append(zipcode if zipcode else "<MISSING>")
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone if phone else "<MISSING>")
            tem_var.append(types if types else "<MISSING>")
            tem_var.append(latitude if latitude else "<MISSING>")
            tem_var.append(longitude if longitude else "<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(page_url if page_url else "<MISSING>")
            return_main_object.append(tem_var) 
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
