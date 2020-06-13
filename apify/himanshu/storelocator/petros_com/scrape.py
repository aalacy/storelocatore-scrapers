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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://www.petros.com/locations/"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    # k = soup.find("div",{"class":"one_third"})
    # soup1= BeautifulSoup(,"lxml")
    op = str(soup).split('<div class=""><div class="one_third">')[1].split('<div class="one_third last_column">')[0].replace("</div>",'')
    soup1= BeautifulSoup(op,"lxml")
    # print(soup1)


    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    k = soup.find("div",{"dir":"ltr"})
    # for i in k:
    p = k.find_all("p")
    for p1 in p:
        tem_var =[]
        if "Section 121" in list(p1.stripped_strings) or "Neyland Stadium" in list(p1.stripped_strings) :
            pass
        else:
            full =list(p1.stripped_strings)
            if full[0]=="TEMPORARILY CLOSED DUE TO COVID:":
                del full[0]
            name = full[0]
            street_address = full[1]
            
            phone = list(p1.stripped_strings)[-1]
            city = full[2].split(',')[0]
            state = full[2].split(',')[1].split( )[0]
            zipcode = full[2].split(',')[1].split( )[1]
            full.insert(0,"Hours")
            hours = " ".join(" ".join(full[4:-1]).split("Hours:")[1:]).strip().replace("*Note: Dining room closes one hour earlier than close time",'')
            
            tem_var.append("https://www.petros.com/")
            tem_var.append(name)
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours if hours else "<MISSING>")
            tem_var.append("<MISSING>")
            # print(tem_var)
            yield tem_var

    k = soup.find("div",{"class":"one_third last_column"})
    p = k.find_all("p")

    for p1 in p:
        tem_var =[]
        if "SOUTHERN PINES (Coming Spring 2020)" in list(p1.stripped_strings) or "10725 S US Hwy 15 501 North" in list(p1.stripped_strings) :
            pass
        else:
            full =list(p1.stripped_strings)
            if len(full) != 0:
                hours = " ".join(full[-3:-1]).replace("Unit A Southern Pines, NC 28387",'<MISSING>')
                name = full[0]
                street_address = " ".join(full[1:3])
                phone = list(p1.stripped_strings)[-1]
                city = full[-4].split(',')[0]
                state = full[-4].split(',')[1].split( )[0]
                zipcode = full[-4].split(',')[1].split( )[1]
                
                tem_var.append("https://www.petros.com/")
                tem_var.append(name)
                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode.strip())
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours if hours else "<MISSING>")
                tem_var.append("<MISSING>")

                yield tem_var
            
                # print(tem_var)
            
    p = soup1.find_all("p")
    for p1 in p:
        tem_var =[]
        if "Section 121" in list(p1.stripped_strings) or "Neyland Stadium" in list(p1.stripped_strings) :
            pass
        else:
            full =list(p1.stripped_strings)
            
            if full[0]=="TEMPORARILY CLOSED DUE TO COVID:":
                del full[0]
            street_address=''
            if full[1][0].isdigit():
         
                # print(full)
                name = full[0]
                street_address = full[1]
                
                # replace("Phone number coming soon","<MISSING>")
                phone = list(p1.stripped_strings)[-1]
                city = full[2].split(',')[0]
                state = full[2].split(',')[1].split( )[0]
                zipcode = full[2].split(',')[1].split( )[1]
                full.insert(0,"Hours")
                hours = " ".join(" ".join(full[4:-1]).split("Hours:")[1:]).strip().replace("*Note: Dining room closes one hour earlier than close time",'')
            else:
                street_address = full[0]
                # print("street_address",street_address)
                phone = list(p1.stripped_strings)[-1]
                city = full[1].split(',')[0]
                name = city
                state = full[1].split(',')[1].split( )[0]
                zipcode = full[1].split(',')[1].split( )[1]
                # full.insert(0,"Hours")
                hours = " ".join(" ".join(full[4:-1]).split("Hours:")[1:]).strip().replace("*Note: Dining room closes one hour earlier than close time",'')
            # print(street_address)
            tem_var.append("https://www.petros.com/")
            tem_var.append(name)
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours if hours else "<MISSING>")
            tem_var.append("<MISSING>")
            yield tem_var

   
            

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


