import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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

    base_url= "https://www.costulessdirect.com/resources/locations/"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    hours =[]
    k = soup.find_all("div",{"class":"main_content"})
   
    for i in k:
        name = i.find_all("h2",{"itemprop":"name"})

        for n in name:
            tem_var=[]
            name=(n.text.replace('\n',""))
            base_url1= n.a['href']
            r = requests.get(base_url1,headers=headers)
            soup1= BeautifulSoup(r.text,"lxml")
            k1=soup1.find("div",{"class":"content_profile"})

            st=list(k1.stripped_strings)[1]
            city = list(k1.stripped_strings)[2]
            state = list(k1.stripped_strings)[4]
            zip1 = list(k1.stripped_strings)[6]
            phone = list(k1.stripped_strings)[10]

            v= list(k1.stripped_strings)
            stopwords ='Parking Lot'
            new_words = [word for word in v if word not in stopwords]

            stopwords ='Parking:'
            new_words2 = [word for word in new_words if word not in stopwords]
            phone  = new_words2[10]
            v1= new_words2[12:]
            if v1[-1]=="English,Spanish":
                del v1[-1]
            if v1[-1]=="Language Spoken:":
                del v1[-1]
            if v1[-1]=="English, Spanish":
                del v1[-1]
            if v1[-1]=="Language Spoken:":
                del v1[-1]

            if v1[0] !="Office Hours:":
                del v1[0]
            hours = (v1)
            
        tem_var.append("https://www.costulessdirect.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("costulessdirect")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours)
        return_main_object.append(tem_var)
   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
