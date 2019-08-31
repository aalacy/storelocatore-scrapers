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
    base_url = "https://www.nutritionzoneusa.com/Store-Locator"
    r = requests.get(base_url)
    main_soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    ds = main_soup.find("table",{"class":"service-center"})
    info =ds.find_all('div',{'class':"service-info"})
    
    for i in info:
        tem_var=[]
        data = list(i.stripped_strings)
        if "COMING SOON!" in data:
            pass
        else:
            stopwords="Address"
            new_words = [word for word in data if word not in stopwords]
            
            
            if len(new_words)==5:
                name = new_words[0]
                store_name.append(name)
                street_address = new_words[1].split(',')
                if len(street_address) == 3:
                    street_address1 = street_address[0]
                    city = street_address[1].replace("#102 ","")
                    state_zip =  street_address[2].split( )
                    state=  state_zip[0]
                    phone = new_words[3]
                    hours_of_operation = new_words[4]
                    if len(state_zip)==2:
                       zipcode =state_zip[1]   
                    else:
                       zipcode="<MISSING>"
                   
                    tem_var.append(street_address1)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("nutritionzoneusa")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append(hours_of_operation)
                    store_detail.append(tem_var)
                   
                elif len(street_address)==2:
                    city1 = street_address[0].split( )
                    if "Diego" in city1:
                        city =city1[3] + ' '+city1[4]
                    else:
                        city = city1[4]
                    phone = new_words[3]
                    tem_var.append(street_address[0])
                    tem_var.append(city)
                    tem_var.append(street_address[1].split()[0])
                    tem_var.append(street_address[1].split()[1])
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("nutritionzoneusa")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append(new_words[4])
                    store_detail.append(tem_var)
                    

                elif len(street_address)==4:
                    street_address1 = street_address[0] +'' +street_address[1]
                    city =  street_address[2]
                    state_zip= street_address[3].split( )
                    state=state_zip[0]
                    zipcode = state_zip[1]

                    phone = new_words[3]
                    tem_var.append(street_address1)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("nutritionzoneusa")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append(new_words[4])
                    store_detail.append(tem_var)
                    

            elif len(new_words)==9:
                name = new_words[0]
                store_name.append(name)
                street_address1 = new_words[1].replace(", Escondido, CA 92025",'')
                city1 = new_words[2]
                
                if "Phone" in city1:
                    city = new_words[1].split(',')[1].replace(" ",'')
                    state =new_words[1].split(',')[2].split( )[0]
                    zipcode = new_words[1].split(',')[2].split( )[1]
                else:
                    city = city1.split(',')[0]
                    state=city1.split(',')[1].split( )[0]
                    zipcode = city1.split(',')[1].split( )[1]
                
                phone1 = new_words[3]

                if "Phone" in phone1:
                    phone = new_words[4]
                    
                else:
                    phone =phone1
               
                time = new_words[5] + ' '+ new_words[6] +' '+new_words[7]+' '+new_words[8]

                
                tem_var.append(street_address1)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("nutritionzoneusa")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(time)
                store_detail.append(tem_var)

            elif len(new_words)==4:
                name = new_words[0]
                store_name.append(name)
                street_address1 = new_words[1]
                city = new_words[2].split(',')[0]
                state=new_words[2].split(',')[1].split( )[0]
                zipcode1 = new_words[2].split(',')[1].split( )[1]
                phone = new_words[3].replace("T. ",'')
                
                tem_var.append(street_address1)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("nutritionzoneusa")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                store_detail.append(tem_var)
            
            elif len(new_words)==8:
                name = new_words[0]
                store_name.append(name)
                street_address1 = new_words[1].split(',')[0].replace(" Raleigh","")
                city1 = "Raleigh"
                state = new_words[1].split(',')[1].split( )[0]
                zipcode1=new_words[1].split(',')[1].split( )[1]
                phone = new_words[3]
                time = new_words[4]+' '+new_words[5]+' '+new_words[6]+' '+new_words[7]

                tem_var.append(street_address1)
                tem_var.append(city1)
                tem_var.append(state)
                tem_var.append(zipcode1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("nutritionzoneusa")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(time)
                store_detail.append(tem_var)
    
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.nutritionzoneusa.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
                  
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
