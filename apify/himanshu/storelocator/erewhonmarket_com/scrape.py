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
    base_url= "https://www.erewhonmarket.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    

    
    
    k=(soup.find_all("table",{"role":"presentation"}))
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone =[]
    latitude =[]
    longitude=[]
    k1 = soup.find_all("iframe")
    k2 = soup.find_all("div",{"id":"pages-container-one"})
    for j in k2:
        a= j.find_all("a",{'href':re.compile('^tel')})
        for a1 in a:
            phone.append(a1.text)

    for j in k1:
        
        if len(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d"))!=1:
            latitude.append(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d")[1])
            longitude.append(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d")[0])
        else:
            latitude.append(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d")[0].split(',')[0])
            longitude.append(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d")[0].split(',')[1])
       
       
    for index,i in enumerate(k):
      
        if  list(i.stripped_strings) !=[]:

            tem_var=[]
            
            st = list(i.stripped_strings)[0]
            city = list(i.stripped_strings)[1].split(',')[0]
            state = list(i.stripped_strings)[1].split(',')[1].split( )[0]
            zip1 = list(i.stripped_strings)[1].split(',')[1].split( )[1]
            hours = (" ".join(list(i.stripped_strings)[-2:]).split('com')[-1])
            store_name.append(city)
          
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone[index])
            tem_var.append("erewhonmarket")
            tem_var.append(latitude[index])
            tem_var.append(longitude[index])
            tem_var.append(hours)
            store_detail.append(tem_var)


    for i in range(len(store_name)):
        store = list()
        store.append("https://www.erewhonmarket.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
