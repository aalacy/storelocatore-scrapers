import csv
import requests
from bs4 import BeautifulSoup
import re
import json
requests.packages.urllib3.disable_warnings()

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

    base_url= "https://www.sagebrushsteakhouse.com/north-carolina"
    r = requests.get(base_url,verify=False)
    soup1= BeautifulSoup(r.text,"lxml")
    

    store_name=[]
    store_detail=[]
    return_main_object=[]
    hours =[]
    k1  =soup1.find_all("ul",{"class":"subnavigation"})
    phone =[]
    page_url = []
    for a in k1:
        a1 = a.find_all("li",{"class":"js-subpage"})
        for link in a1:
            if "KENTUCKY" in link.a.text or "NORTH CAROLINA" in link.a.text or "TENNESSEE" in link.a.text or "VIRGINIA" in link.a.text :
                page_url1=link.a['href']
                
                # print(page_url)
                r = requests.get(link.a['href'])
                soup= BeautifulSoup(r.text,"lxml")
                k = soup.find_all("div",{"id":"ctl01_pSpanDesc","class":"t-edit-helper"})
                names =soup.find_all('h4',{"class":"align-left biz-address fp-el"})

                for name in names:
                    new=(name.text.replace("BOONE","SAGEBRUSH OF BOONE").replace("LENOIR","SAGEBRUSH OF LENOIR").replace("SHELBY","SAGEBRUSH OF SHELBY"))
                    if "SAGEBRUSH OF" in new:
                        new1 =new.split("SAGEBRUSH OF")
                        if new1[-1]:
                            store_name.append("SAGEBRUSH OF".join(new.split("SAGEBRUSH OF")))
                    else:
                        store_name.append(new)
                        

                for i in k:
                    p =i.find_all('p')
                    tem_var =[]
                    if p != []:
                        page_url.append(page_url1)
                        street = (p[1].text)
                        phone.append(p[0].text.replace("PHONE - ",""))
                        city = p[2].text.split(',')[0]
                        state = p[2].text.split(',')[1].split( )[0]
                        zipcode = p[2].text.split(',')[-1].split( )[-1]

                        tem_var.append(street)
                        tem_var.append(city)
                        tem_var.append(state.strip())
                        tem_var.append(zipcode.strip())
                        store_detail.append(tem_var)

                    for index,j in enumerate(p[:-4]):
                        time = ''
                        if index==4:
                            if "Catering Menus" in j.text:
                                time = '<MISSING>'
                            else:
                                time = (j.text)
                            hours.append(time)

   
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.sagebrushsteakhouse.com")
        store.append(store_name[i].encode('ascii', 'ignore').decode('ascii').strip())
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(" ".join(phone[i].split('-')[1:]).encode('ascii', 'ignore').decode('ascii').strip())
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours[i].encode('ascii', 'ignore').decode('ascii').strip())
        store.append(page_url[i])
       
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
