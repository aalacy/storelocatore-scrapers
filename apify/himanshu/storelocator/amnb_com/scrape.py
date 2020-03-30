import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast


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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://www.amnb.com/_/api/branches/36.5868855/-79.39516750000001/50"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    
    
    
    base_url1= "https://www.amnb.com/_/api/atms/36.5868855/-79.39516750000001/50"
    r = session.get(base_url1,headers=headers)
    soup1= BeautifulSoup(r.text,"lxml")


    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone = []
    hours =[]
   
    # time = soup.find_all("div",{"class":"col-7 col-md-7 claro"})
    # pattern = re.compile(r"window.Rent.data\s+=\s+(\{.*?\});\n")
    # data = (soup.find("script",{"type":"application/ld+json"}))

    data = (json.loads(soup.text))

    data1 = (json.loads(soup1.text))

    for  i in data['branches']:
        tem_var =[]
        # print(i)
        store_name.append(i['name'])
        street_address = i["address"]
        city = i["city"]
        state = i["state"]
        zipcode = i["zip"]
        phone = i["phone"]
       
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zipcode.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone if phone else "<MISSING>")
        tem_var.append("branches")
        tem_var.append(i["lat"])
        tem_var.append(i['long'])
        tem_var.append(i["description"].replace("ATM available during business hours"," ").replace("Hours:","").strip().replace("."," ").replace("Drive-Thru Mon"," Drive-Thru Mon").replace("24 Hour ATM"," 24 Hour ATM"))
        # print()
        store_detail.append(tem_var)
     
        
    for  i in data1['atms']:
        tem_var =[]
        
        store_name.append(i['name'])
        street_address = i["address"]
        city = i["city"]
        state = i["state"]
        zipcode = i["zip"]
        phone = "<MISSING>"
        
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zipcode.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone if phone else "<MISSING>")
        tem_var.append("atms")
        tem_var.append(i["lat"])
        tem_var.append(i['long'])
        tem_var.append("<MISSING>")
        store_detail.append(tem_var)


    for i in range(len(store_name)):
        store = list()
        store.append("https://www.amnb.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


