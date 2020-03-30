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
    base_url= "https://www.eggspectation.com/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    data = soup.find("ul",{"class":"dropdown"})
    for d in data:
        # print(d.find("a")['href'])
        r1 = session.get(d.find("a")['href'])
        soup1= BeautifulSoup(r1.text,"lxml")
        st = soup1.find("span",{'class':'address-1'}).text
        city = soup1.find("span",{'class':'city'}).text
        state = soup1.find_all("span",{'class':'city'})[-1].text
        zip1 = soup1.find("span",{'class':'zip'}).text
        
        try:
            phone  = soup1.find("a",{'class':'phone-number'}).text
        except:
            phone = ''

        name  = soup1.find("div",{'class':'column column-2'}).find("h2").text
        # print(name.strip())
        try:
            hours =  " ".join(list(soup1.find("div",{'class':'hours-wrapper'}).stripped_strings))
        except:
            hours =''    
   
        tem_var =[]
        tem_var.append("https://www.eggspectation.com/")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone if phone else "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours if hours else "<MISSING>")
        tem_var.append(d.find("a")['href'])
        # print(tem_var)
        return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


