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
    base_url= "https://hghills.com/locations"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
  
    name_store=[]
    store_detail=[]
    phone=[]
    return_main_object=[]

    k=soup.find_all("table",{"class":"locationstable","cellspacing":"0"})

    for i in k:
        name = i.find_all("h5")
        name1 = i.find_all("ul",{"class":"storeaddress"})
       
        for j in name:
            name_store.append(j.text)
            
        for index,j in enumerate(name1):
            tem_var=[]
            st =list(j.stripped_strings)[0]
            city =list(j.stripped_strings)[1].split(",")[0]
            state = list(j.stripped_strings)[1].split(",")[1].split( )[0]
            zipcode = list(j.stripped_strings)[1].split(",")[1].split( )[1]
            phone =list(j.stripped_strings)[2]

            if len(list(j.stripped_strings)[3:][:-2])==1:
                hours = "<MISSING>"
            else:
                hours=(" ".join(list(j.stripped_strings)[4:][:-2]).replace("Show On Map Weekly Ads",""))
    

            tem_var.append("https://hghills.com")
            tem_var.append(name_store[index])
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("hghills")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours)
            return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
