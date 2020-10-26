import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('erewhonmarket_com')


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
        a= j.find_all("a",{'href':re.compile('tel')})
        for a1 in a:
            phone.append(a1.text.replace("CBS Television City","424.433.8111"))
    for j in k1:      
        if len(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d"))!=1:
            latitude.append(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d")[1])
            longitude.append(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d")[0])
        else:
            latitude.append(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d")[0].split(',')[0])
            longitude.append(j.attrs['src'].split("!2d")[-1].split("&ll=")[-1].split("!2m")[0].split("&spn")[0].split("!3d")[0].split(',')[1])    
    
    phone[3]="310.362.3062"
    phone[4]="310.561.8898"
    #logger.info(phone)
    for index,i in enumerate(k):
        if  list(i.stripped_strings) !=[]:
            tem_var=[]
            st = (list(i.stripped_strings)[0]).replace("Corporate Office","2430 E 11 Th Street")
            data = (list(i.stripped_strings)[1]).replace("2430 E 11 Th Street","Los Angeles, CA 90023")
            city = data.split(',')[0]
            state =  data.split(',')[1].split(" ")[1]
            zipp = data.split(',')[1].split(" ")[-1]
            if (len(list(i.stripped_strings))) == 3:
                if "90026" in zipp:
                    hours = "Opening summer 2020"
                else:
                    hours = "<MISSING>"
            else:
                hours = (" ".join(list(i.stripped_strings)[-15:]).split('com')[-1]).strip()
            if "90026" in zipp:
                continue
            store_name.append(city)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipp)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone[index] if phone[index] else "<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(latitude[index])
            tem_var.append(longitude[index])
            tem_var.append(hours)
            tem_var.append(base_url)
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

