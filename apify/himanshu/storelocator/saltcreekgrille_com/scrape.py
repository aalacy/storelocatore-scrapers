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
    base_url= "https://saltcreekgrille.com"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    k=soup.find("ul",{"class":"sub-menu"})
    a = k.find_all("a")
    for i in a:
        tem_var =[]
        base_url1= i['href']
        r = session.get(base_url1)
        soup1= BeautifulSoup(r.text,"lxml")
        k1 = soup1.find("div",{"class":"column col-sm-6"})
        v = list(k1.stripped_strings)
        stopwords = 'Hours'
        new_words = [word for word in v if word not in stopwords]
        street_address = new_words[1]
        city =  new_words[2].split(',')[0]
        state = new_words[2].split(',')[1].split( )[0]
        zipcode = new_words[2].split(',')[1].split( )[1]
        phone  = new_words[3]
        hours =  " ".join(new_words[4:]).replace("Happenings","")
        
        tem_var.append(street_address)
        tem_var.append("https://saltcreekgrille.com")
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zipcode.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("saltcreekgrille")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours)
        return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
