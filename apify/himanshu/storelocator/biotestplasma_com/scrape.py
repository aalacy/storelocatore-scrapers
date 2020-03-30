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
    base_url= "https://biotestplasma.com/find-plasma-center-near/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= soup.find_all("section",{"class":"grid-container"})
   
   
    for i in k:
        cell = i.find_all("div",{"class":"cell"})
        # print(len(cell))
        for j in cell:
            tem_var=[]
            if "Athens-Atlanta Highway - Coming Soon!" in j.a.text:
                pass
            else:
                # print(j.a['href'])
                r = session.get(j.a['href'])
                soup1= BeautifulSoup(r.text,"lxml")
                lat = soup1.find("section",{'class':"entry-content"}).find("div",{"class":"marker"}).attrs['data-lat']
                lng = soup1.find("section",{'class':"entry-content"}).find("div",{"class":"marker"}).attrs['data-lng']
                v1 = list(soup1.find("section",{'class':"entry-content"}).stripped_strings)

                if "5915 1st Avenue" in v1:
                    name = v1[0]
                    st = v1[2]
                    city= v1[3].split(',')[0]
                    state = v1[3].split(',')[1].split( )[0]
                    zip1 = v1[3].split(',')[1].split( )[1]
                    phone  = v1[4]
                    hours = (" ".join(v1[5:]).replace("Hours:","").replace("Schedule Today!",""))
                else:
                    
                    hours = " ".join(v1[-4:]).replace("'Hours:","").replace("Schedule Today!","").replace("Walk In Only!","")

                    if  v1[-5]=="Hours:":
                        del v1[-5]
                    phone = v1[-6]
                    city = v1[-7].split(",")[0]
                    state = " ".join(v1[-7].split(",")[1].split( )[:-1])
                    zip1 = v1[-7].split(",")[1].split( )[-1]
                    st = v1[-8]
                    name = v1[-10]



                tem_var.append("https://biotestplasma.com")
                tem_var.append(name)
                tem_var.append(st)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("biotestplasma")
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


