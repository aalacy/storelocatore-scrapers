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
    
    base_url = "http://www.emackandbolios.com/mastores/"
    r = requests.get(base_url)
    main_soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]

    link = main_soup.find("div",{"id":"tabNav","class":"menu-shop-locations-menu-container"})
    a = link.find_all("a")
    
    for i in a:
        if re.search("Int’l",i.text):
            pass
        elif re.search("FL",i.text):
            r = requests.get(i['href'])
            soup= BeautifulSoup(r.text,"lxml")
            data = soup.find("div",{"class":"entry-content group"})
            names =(data.find_all('h2') [len(data.find_all('h2'))-1])
            store_name.append(names.text)
            info = data.find_all("p")
            for j in info:
                temp_var =[]
                if list(j.stripped_strings) !=[]:
                    city = list(j.stripped_strings)[0].split(',')[0]

                    street_address = "<MISSING>"
                    state = list(j.stripped_strings)[0].split(',')[1].split( )[0]
                    zipcode = list(j.stripped_strings)[0].split(',')[1].split( )[1]
                    phone = list(j.stripped_strings)[1]
                    temp_var.append(street_address)
                    temp_var.append(city)
                    temp_var.append(state)
                    temp_var.append(zipcode)
                    temp_var.append("US")
                    temp_var.append("<MISSING>")
                    temp_var.append(phone)
                    temp_var.append("emackandbolios")
                    temp_var.append("<MISSING>")
                    temp_var.append("<MISSING>")
                    temp_var.append("<MISSING>")
                    store_detail.append(temp_var)
                        

        else:
            r = requests.get(i['href'])
            soup= BeautifulSoup(r.text,"lxml")
            data = soup.find("div",{"class":"entry-content group"})
            info = data.find_all("p")
            for i in info:
                temp_var =[]
                phone =''
                if list(i.stripped_strings) !=[]:
                    if len(list(i.stripped_strings)) ==1:
                        pass
                    else:
                        if "Amsterdam Ave" in list(i.stripped_strings) or "Brooklyn Heights" in list(i.stripped_strings):
                            street_address1 = list(i.stripped_strings)[1]
                            
                            if "Between 78th & 79th" in street_address1:
                                street_address = "<MISSING>"
                            
                            else:
                                street_address = street_address1
                                

                            store_name.append(street_address1)
                            city = list(i.stripped_strings)[2].split(',')[0]
                            state =list(i.stripped_strings)[2].split(',')[1].split( )[0]
                            zipcode = list(i.stripped_strings)[2].split(',')[1].split( )[1]
                            phone = list(i.stripped_strings)[3]

                            temp_var.append(street_address)
                            temp_var.append(city)
                            temp_var.append(state)
                            temp_var.append(zipcode)
                            temp_var.append("US")
                            temp_var.append("<MISSING>")
                            temp_var.append(phone)
                            temp_var.append("emackandbolios")
                            temp_var.append("<MISSING>")
                            temp_var.append("<MISSING>")
                            temp_var.append("<MISSING>")
                            store_detail.append(temp_var)
                            

                        else:
                            street_address1 = list(i.stripped_strings)[0]

                            if "Popponesset Marketplace" in street_address1 or "Peoria Riverfront Visitor Center" in street_address1 or "North Station" in street_address1:
                                street_address = "<MISSING>"
                            else:
                                street_address =street_address1

                            store_name.append(street_address1)
                            city = list(i.stripped_strings)[1].split(',')[0]
                            state = list(i.stripped_strings)[1].split(',')[1].split( )[0]
                            zipcode = list(i.stripped_strings)[1].split(',')[1].split( )[1]
                            if len(list(i.stripped_strings)) == 4:
                                phone = list(i.stripped_strings)[2]
                            elif len(list(i.stripped_strings)) == 3:
                                phone = list(i.stripped_strings)[2]
                            elif len(list(i.stripped_strings)) == 2:
                                phone = '(908) 228-3967'

                            
                            temp_var.append(street_address)
                            temp_var.append(city)
                            temp_var.append(state)
                            temp_var.append(zipcode)
                            temp_var.append("US")
                            temp_var.append("<MISSING>")
                            temp_var.append(phone)
                            temp_var.append("emackandbolios")
                            temp_var.append("<MISSING>")
                            temp_var.append("<MISSING>")
                            temp_var.append("<MISSING>")
                            store_detail.append(temp_var)
        
            
    for i in range(len(store_name)):
        store =  list()
        store.append("http://www.emackandbolios.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    print(return_main_object)
    data = soup.find("div",{"class":"entry-content group"})

    info = data.find_all("p")

    # for i in info:
    #     if list(i.stripped_strings) !=[]:
    #         print(list(i.stripped_strings) )
    
    

   
    
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
