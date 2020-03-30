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
    base_url= "https://www.mybankcnb.com/Locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    lat =[]
    lng =[ ]
    hours =[]
    k=soup.find_all("tr",{"class":"individualLocation"})

    for i in k:
        tem_var =[]
       
        store_name.append(i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[0] + "Branch")
        street_address = (i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[1].split('  ')[0])
        phone = (" ".join(i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[1].split('  ')[1].split( )[-2:]).replace("KS 67335","<MISSING>")) 
        
        if "Cherryvale" in (i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[1].split('  ')[1].split( )):
            city = (i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[1].split('  ')[1].split( )[0])
            state  = (i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[1].split('  ')[1].split( )[1])
            zipcode = (i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[1].split('  ')[1].split( )[2])
            lat.append(list(i.stripped_strings)[-1])
            lng.append(list(i.stripped_strings)[-1])

            r = session.get(list(i.stripped_strings)[-3])
            soup1= BeautifulSoup(r.text,"lxml")
            hours.append(" ".join(list(soup1.find("td",{"width":"50%"}).stripped_strings)[-3:]))

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("mybankcnb")
            store_detail.append(tem_var)

        else:
            lng.append(list(i.stripped_strings)[-1])
            lat.append(list(i.stripped_strings)[-2])
            zipcode = (i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[1].split('  ')[1].split( )[:-2][-1])
            state = i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[1].split('  ')[1].split( )[:-2][-2]
            city = " ".join(i.text.replace("\n"," ").split("   ")[0].split("Branch",1)[1].split('  ')[1].split( )[:-4])

            
            r = session.get(list(i.stripped_strings)[-3])
            soup3= BeautifulSoup(r.text,"lxml")
            h2 = soup3.find("td",{"width":"50%"})
            h3 = soup3.find("td",{"style":"width: 50%;"})
            if h2 != None:
                v= list(soup3.find("td",{"width":"50%"}).stripped_strings)[-4:]
                v1 = [words.replace("\xa0","").replace("n/a","") for words in v ]
                hours.append(" ".join(v1).replace("F: (580) 765-0615",""))
                # print(list(soup3.find("td",{"width":"50%"}).stripped_strings))
            else:
                hours.append(" ".join(list(h3.stripped_strings)[-4:]))
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("mybankcnb")
            store_detail.append(tem_var)
            
   
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.mybankcnb.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(lat[i])
        store.append(lng[i])
        store.append(hours[i])
     
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


