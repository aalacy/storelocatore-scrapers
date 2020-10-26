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
  
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://www.ebgames.ca/StoreLocator/GetStoresForStoreLocatorByProduct?value=&skuType=0&language=en-CA"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")

    name_store=[]
    store_detail=[]
    phone=[]
    lat =''
    log=''
    return_main_object=[]
    k=json.loads(soup.text,strict=False)
    for index,i in enumerate(k):
        tem_var=[]

        if index!=0:
            st = i['Address']
            if "Latitude" in i:
                lat = i['Latitude']
                print(lat)
            else:
                lat = "<MISSING>"

            if "Longitude" in i:
                log =i['Longitude']
            else:
                log ="<MISSING>"

            postal =i['Zip']
            name = i['Name']
            
            if len(postal)!=5:
                country = "CA"
            else:
                country = "US"
            
            state =i['Province']
            city =i['City']
            phone1 =i["Phones"]  

            if "Please call this store for operating hours." in i['Hours']:
                hours = "<MISSING>"
            else:
                hours = i['Hours'].replace("<br>","")
                

            if len(phone1)==1:
                phone="<MISSING>"
            else:
                phone=phone1

           
            tem_var.append("https://www.ebgames.ca")
            tem_var.append(name.replace("\x8f",""))
            tem_var.append(st.replace("\x8f",""))
            tem_var.append(city.replace("\x8f","").replace("undefined","<MISSING>"))
            tem_var.append(state.replace("\x8f","").replace("undefined","<MISSING>"))
            tem_var.append(postal.replace("\x8f","").replace("_",""))
            tem_var.append(country)
            tem_var.append("<MISSING>")
            tem_var.append(phone.replace("\x8f","").replace("undefined","<MISSING>"))
            tem_var.append("ebgames.ca")
            
            tem_var.append(lat.replace("undefined","<MISSING>"))
            tem_var.append(log.replace("undefined","<MISSING>"))
            tem_var.append(hours.replace("\x8f",""))
            return_main_object.append(tem_var)
       
   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




