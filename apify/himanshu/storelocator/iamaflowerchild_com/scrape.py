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
  
    base_url= "https://www.iamaflowerchild.com/locations/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    a=soup.find_all("a",{"class":"button"})

    for index,a1 in enumerate(a):
        if  index ==17:
            pass
        else:
            tem_var =[]
            if a1['href'].replace("/locations/","").replace("https://order.iamaflowerchild.com/home/",""):
                city = ''
                r = requests.get(a1['href'])
                soup1= BeautifulSoup(r.text,"lxml")
                k1=(soup1.find_all("script")[5].text)
                h1 = soup1.find("ul",{"class":"location-hours"})
                
                
                if h1 != None:
                    hours = (list(h1.stripped_strings)[-1])
                else:
                    hours = ("<MISSING>")
                
                k= json.loads(k1)
                
                if "addressRegion" in k['address'] or k['address']['addressRegion'] != None:
                    state = (k['address']['addressRegion'])
                else:
                    state = ("<MISSING>")

                
                if "streetAddress" in k['address']:
                    st = (k['address']['streetAddress'])
                else:
                    st = ("<MISSING>")


                if "postalCode" in k['address'] or k['address']['postalCode'] != None:
                    zip1 = (k['address']['postalCode'])
                else:
                    zip1 = ("<MISSING>")

                if "addressLocality" in k['address'] or k['address']['addressLocality'] != None:
                    city = (k['address']['addressLocality'])
                else:
                    city = ("<MISSING>")

            

                if "telephone" in k:
                
                    phone = k['telephone']
                else:
                    phone = "<MISSING>"


                if "latitude" in k['geo'] or k['geo']['latitude'] != None:
                    lat = (k['geo']['latitude'])
                else:
                    lat = ("<MISSING>")

                if "longitude" in k['geo'] or k['geo']['longitude'] != None:
                    log = (k['geo']['longitude'])
                else:
                    log = ("<MISSING>")

                tem_var.append("https://www.iamaflowerchild.com")
                tem_var.append(city)
                tem_var.append(st)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("iamaflowerchild")
                tem_var.append(lat)
                tem_var.append(log)
                tem_var.append(hours)
                return_main_object.append(tem_var)
        
    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


