import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast


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
    base_url= "https://santamonicaseafood.com/contact"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
  
    store_name=[]
    store_detail=[]
    return_main_object=[]
    latitude1 =[]
    longitude1=[]
    hours1=[]
    k = soup.find_all("div",{"class":"x-column x-sm vc x-1-2"})

    base_url1= "http://www.smseafoodmarket.com/santa-monica-seafood-market-and-cafe/"
    r = session.get(base_url1,headers=headers)
    soup1= BeautifulSoup(r.text,"lxml")

    k1 = soup1.find("div",{"class":"x-column x-sm vc x-1-2"}).find("p")
    latitude1.append(k1.a['href'].split("@")[1].split(",15")[0].split(',')[0])
    longitude1.append(k1.a['href'].split("@")[1].split(",15")[0].split(',')[1])
    
    if k1.text.replace("Santa Monica Seafood – Santa Monica",""):
        hours1.append(k1.text.replace("Santa Monica Seafood – Santa Monica","").replace("\n",""))
      
    


    base_url2= "http://www.smseafoodmarket.com/costa-mesa-seafood-market-and-cafe/"
    r = session.get(base_url2,headers=headers)
    soup2= BeautifulSoup(r.text,"lxml")

    k2 = soup2.find("div",{"class":"wpb_wrapper"})
    latitude1.append(k2.a['href'].split("ll=")[1].split("&sspn=0")[0].split(',')[0])
    longitude1.append(k2.a['href'].split("ll=")[1].split("&sspn=0")[0].split(',')[1])
    if k2.text.replace("View Café Menu Market Specials","").replace("Shop in Our Market or Dine in Our Café and Oyster Bar","").replace("Santa Monica Seafood – Costa Mesa",""):
        hours = (k2.text.replace("Shop in Our Market or Dine in Our Café and Oyster Bar","").replace("View Café Menu Market Specials","").replace("Shop in Our Market or Dine in Our Café and Oyster Bar","").replace("Santa Monica Seafood – Costa Mesa",""))
        hours1.append(hours.replace("\n","").split(',,')[0].replace("Shop in Our Market or Dine in Our\xa0Café and Oyster Bar",""))
       




    for i in k:
        p = i.find_all("p")

        for p1 in p:
            tem_var=[]
            if len(list(p1.stripped_strings)) !=1:

                if len(list(p1.stripped_strings))==5:
                    phone= "  ".join(list(p1.stripped_strings)).replace(" Fax: (702) 492-2300","").split('  ')[-1].replace("Phone: ","")
                    city ="  ".join(list(p1.stripped_strings)).replace(" Fax: (702) 492-2300","").split('  ')[-2].split(",")[0]
                    state ="  ".join(list(p1.stripped_strings)).replace(" Fax: (702) 492-2300","").split('  ')[-2].split(",")[1].split( )[0]
                    zip1 = "  ".join(list(p1.stripped_strings)).replace(" Fax: (702) 492-2300","").split('  ')[-2].split(",")[1].split( )[1]
                    st = "  ".join(list(p1.stripped_strings)).replace(" Fax: (702) 492-2300","").split('  ')[-3]
                    name = " ".join("  ".join(list(p1.stripped_strings)).replace(" Fax: (702) 492-2300","").split('  ')[:-3])

                    store_name.append(name)
                    tem_var.append(st)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("santamonicaseafood")
                    store_detail.append(tem_var)
                    
                elif len(list(p1.stripped_strings))==7:
                    name = " ".join(list(p1.stripped_strings)[:2])
                    st = list(p1.stripped_strings)[2]
                    city = list(p1.stripped_strings)[3].split(',')[0]
                    state = list(p1.stripped_strings)[3].split(',')[1].split( )[0]
                    zip1 = list(p1.stripped_strings)[3].split(',')[1].split( )[1]
                    phone ='<MISSING>'

                    store_name.append(name)
                    tem_var.append(st)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("santamonicaseafood")
                    store_detail.append(tem_var)

                elif len(list(p1.stripped_strings))==4:
                    name  = list(p1.stripped_strings)[0]
                    st = list(p1.stripped_strings)[1]
                    city = list(p1.stripped_strings)[2].split(",")[0]
                    state = list(p1.stripped_strings)[2].split(",")[1].split( )[0]
                    zip1 = list(p1.stripped_strings)[2].split(",")[1].split( )[1]
                    phone = list(p1.stripped_strings)[-1].replace("Phone: ","")
                    
                    store_name.append(name)
                    tem_var.append(st)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("santamonicaseafood")
    
                    store_detail.append(tem_var)

  
    
    for i in range(len(store_name)):
        store = list()
        store.append("https://santamonicaseafood.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
