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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url= "https://www.isaacsrestaurants.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k= (soup.find_all("a",{"class":"title"}))

    for i in k:
        tem_var=[]
        base_url= i['href']
        r = session.get(base_url,headers=headers)
        soup1= BeautifulSoup(r.text,"lxml")
        v = list(soup1.find("address").stripped_strings)
        v1 = list(soup1.find("div",{"class":"phones"}).stripped_strings)
        v3 = soup1.find("div",{"class":"linkButton blue inline"})

        name = (soup1.find("h1",{"class":"entry-title"}).text)

        lat = v3.a['href'].split("@")[1].split(',')[0]
        log = v3.a['href'].split("@")[1].split(',')[1]
        

        v2 = list(soup1.find("div",{"class":"hours"}).stripped_strings)
        hours = (" ".join(v2).replace("Click HERE to check out our Happy Hour Specials, Beer Selection and Cocktails & Wine List!","").replace("Hours of Operation:",""))
        phone = v1[1]
        


        if list(soup1.find("address").stripped_strings)[1][0].isnumeric():
            del v[0]
        if v[-1]=="Save":
            del v[-1]
            
        city = v[-1].split(',')[0]
        state = v[-1].split(',')[1].split( )[0]
        zip1 = v[-1].split(',')[1].split( )[1]
        st = (" ".join(v[:-1]).replace("The Shops of Traintown Route",""))
        

        tem_var.append("https://www.isaacsrestaurants.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("isaacsrestaurants")
        tem_var.append(lat)
        tem_var.append(log)
        tem_var.append(hours)
        return_main_object.append(tem_var)

  
    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


