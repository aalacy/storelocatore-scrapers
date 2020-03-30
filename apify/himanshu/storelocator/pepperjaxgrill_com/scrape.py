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
    base_url= "https://pepperjaxgrill.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?t=1565418254545"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    latitude =[]
    longitude=[]
    hours = []
    phone =[]

    st = soup.find_all("address")
    lt = soup.find_all("latitude")
    lg = soup.find_all("longitude")
    names = soup.find_all("location")
    
    description = soup.find_all("description")

    for name in names:
        store_name.append(name.text)

    for description1 in description:
        soup1= BeautifulSoup(description1.text,"lxml")
        d = soup1.find_all("span",{"class":"storeHours"})
        a = soup1.find("a")
        phone.append(a['href'].replace("tel:+1","").replace("tel:",""))
        hours.append(d[0].text.replace("Hours: ",""))
   

    for lt1 in lt:
        latitude.append(lt1.text)
    
    for lg1 in lg:
        longitude.append(lg1.text)

    
    for std in st:
        tem_var =[]
        state = (std.text.split(',')[-1].strip().split( )[0])
        zipcode = (std.text.split(',')[-1].strip().split( )[1])
        city = std.text.split(',')[:-1][0].split('  ')[-1]
        street_address = std.text.split(',')[:-1][0].split('  ')[0]

     
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipcode)
        store_detail.append(tem_var)
        
    
    
    for i in range(len(store_name)):
        store = list()
        store.append("https://pepperjaxgrill.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i])
        store.append("pepperjaxgrill")
        store.append(latitude[i])
        store.append(longitude[i])
        store.append(hours[i])
        return_main_object.append(store) 
  
      
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
