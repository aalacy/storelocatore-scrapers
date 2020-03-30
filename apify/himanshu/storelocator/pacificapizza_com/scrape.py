import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import math
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
    base_url= "https://www.pacificapizza.com/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
  

    link = soup.find_all("p",{"class":"font_8"})
    i = 0
    # return_main_object=[]
    for q in range(int(len(link)/4)):
        name = link[i].text
        name1 = link[i+1].text
        name2= link[i+2].text
        i = i+4
        st = name
        if len(name1)== 17:
            city = name1.split(',')[0]
            state = name1.split(',')[1].split(' ')[1]
            zip1 = name1.split(',')[1].split(' ')[2]
        else :
            city = name1.split(',')[0]
            state = name1.split(',')[1].split(' ')[1]
            zip1 = "<MISSING>"
        phone = name2.replace('(','').replace(')','')
        tem_var =[]
        tem_var.append("https://www.pacificapizza.com")
        tem_var.append("<MISSING>")
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(base_url)
        tem_var = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in tem_var]
        # print(tem_var)
        yield tem_var


    # return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
