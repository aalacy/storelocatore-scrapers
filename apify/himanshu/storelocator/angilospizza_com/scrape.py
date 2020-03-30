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
    base_url= "http://www.angilospizza.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k= soup.find_all("ul",{"class":"locationul"})
    for i in k:
        p = i.find_all("a")
        for i in p:
            tem_var=[]
            r = session.get(i['href'],headers=headers)
            soup1= BeautifulSoup(r.text,"lxml")
            a = soup1.find("div",{"class":"google-maps gm-margin gmlocation"}).iframe
            if a != None:
                lng  = a['src'].split("2d")[1].split("!3d")[0]
                lat = a['src'].split("2d")[1].split("!3d")[1].split("!2m")[0]
            else:
                lat = "<MISSING>"
                lng = "<MISSING>"
            # print(soup1.find("div",{"class":"google-maps gm-margin gmlocation"}).iframe["src"])
            # print(soup1.find_all("div",{"class":"locationc"})[-1])
            k1 = list(soup1.find_all("div",{"class":"locationc"})[-2].stripped_strings)
            words = [w.replace('\xa0', ' ') for w in k1]
            if "1725 Berry Blvd" in words: 
                st = words[1]
                city = words[2].split(',')[0]
                state = words[2].split(',')[1].split( )[0]
                zip1 = words[2].split(',')[1].split( )[1]
                phone  = words[4]
                hours =(" ".join(words[6:]))
            else:
                st = words[1].split(',')[0]
                city = words[1].split(',')[1]
                state = words[1].split(',')[2].split( )[0]
                zip1 = words[1].split(',')[2].split( )[1]
                if words[3]=="36-PIZZA":
                    phone = words[4]
                    hour = words[5:]

                else:   
                    phone = words[3]

                if words[5:] !=[]:
                    hours = (" ".join(words[5:]).replace("Hours of Operation:","<MISSING>").replace(" midnight Delivery Hours Beer delivery available","").replace("Delivery Hours no delivery www.myspace.com/angilospizza","").replace("Delivery Hours same as store hours","").replace(" Delivery Hours Delivery stops 30 minutes prior to closing time. $2 delivery fee","").replace("Delivery Hours We will gladly deliver to your door during our business hours! We are committed to having the fastest delivery in Sharonville.","").replace("<MISSING> ","").replace("Delivery stops 15 minutes prior to close","<MISSING>"))
                else:
                    hours = "<MISSING>"
            tem_var.append("http://www.angilospizza.com")
            tem_var.append(i.text)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("angilospizza")
            tem_var.append(lat)
            tem_var.append(lng)
            tem_var.append(hours)
            print(tem_var)
            return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


