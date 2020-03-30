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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" ,"page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object=[]
    base_url= "https://canada.chevron.com/contact"
    r= session.get(base_url)
    soup=BeautifulSoup(r.text, "lxml")
    a = soup.find_all("div",{"class":"col col-xs-12 col-sm-6 col-md-3"})
    for i in a:
        tem_var=[]
        t=list(i.stripped_strings)
        name=t[0]
        
        if "Telephone:" not in t[-1]:
            del t[-1]
        if "Telephone:" not in t[-1]:
            del t[-1]
        phone=t[-1].replace('Telephone:','').replace('\xa0','')
        del t[-1]
        city=t[-1].split(',')[0]    
                
        state=t[-1].split(',')[1].strip().split(' ')[0] 
    
        zip=" ".join(t[-1].split(',')[1].strip().split(' ')[1:])
        
        del t[-1]
        del t[0]
        
        st=''.join(t[-3:]).replace('(Exploration & Production)','')  
    
          
        tem_var.append("https://canada.chevron.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip)
        tem_var.append("CA")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("https://canada.chevron.com/contact")
        print(tem_var)
        return_main_object.append(tem_var)


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
