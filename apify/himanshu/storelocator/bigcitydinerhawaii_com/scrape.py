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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"

    }
    base_url= "https://bigcitydinerhawaii.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    address=[]
    k= soup.find_all('div',{"class":"wpb_wrapper"})
    
    for i in k:
        tem_var=[]
        if list(i.stripped_strings) !=[]:
            v= list(i.stripped_strings)
            if len(v[1].split(',')[-1].split( ))==2:
                zip1 = v[1].split(',')[-1].split( )[1]
            else:
                zip1 = "<MISSING>"

            state =v[1].split(',')[-1].split( )[0]
            city = " ".join(v[1].split(',')[:-1]).split( )[-1]   
            st =(" ".join(" ".join(v[1].split(',')[:-1]).split( )[:-1]))
            phone = v[-1]
            time = " ".join(v[2:][:-1])
   
            tem_var.append("https://bigcitydinerhawaii.com")
            tem_var.append(list(i.stripped_strings)[0])
            tem_var.append(st.replace("\u02bb",""))
            tem_var.append(city.replace("\u02bb",""))
            tem_var.append(state.replace("\u02bb",""))
            tem_var.append(zip1.replace("\u02bb",""))
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone.replace("\u02bb",""))
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(time.replace("\u02bb",""))
            tem_var.append("<MISSING>")
            if tem_var[3] in address:
                continue
            address.append(tem_var[3])
            return_main_object.append(tem_var)
            

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


