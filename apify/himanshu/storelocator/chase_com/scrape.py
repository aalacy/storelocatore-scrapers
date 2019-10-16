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
    base_url= "https://locator.chase.com/?locale=en_US"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    result =[]
    addresses=[]
    k= soup.find_all("a",{"class":"Directory-listLink"})
   
    for index,i in enumerate(k):
        print(i.text)
        
        if i.text=="Washington, D.C.":
            r = requests.get("https://locator.chase.com/"+i['href'])
            soup7= BeautifulSoup(r.text,"lxml")
            link5 = soup7.find_all("a",{"class":"Teaser-titleLink Link--inverse Text--bold","data-ya-track":"businessname"})

            for l in link5:
                r = requests.get("https://locator.chase.com"+l['href'].replace("..",""))
                soup10= BeautifulSoup(r.text,"lxml")
                name = (soup10.find("h1",{"class":"Core-title"}).text)
                street_address = soup10.find("span",{"class":"c-address-street-1"}).text
                street_address2 = soup10.find("span",{"class":"c-address-street-2"})
                if street_address2 != None:
                    street_address1 = street_address2.text
                city = soup10.find("span",{"class":"c-address-city"}).text
                state1 =  soup10.find("abbr",{"class":"c-address-state"})
                if state1 != None:
                    state = state1.text
                else:
                    state = "<MISSING>"
                zip1 = soup10.find("span",{"class":"c-address-postal-code"}).text
                phone = soup10.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                hours1 = soup10.find("table",{"class":"c-hours-details"})
                time1 = soup10.find("div",{"class":"Core-hoursToday"})
                hours =''
                time=''
                if time1 != None:
                    time ="ATM" +' '+ (" ".join(list(time1.stripped_strings)).replace("Day of the Week Hours",""))
                if hours1 != None:
                    hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))
                latitude = (soup10.find("meta",{"itemprop":"latitude"}).attrs['content'])
                longitude = (soup10.find("meta",{"itemprop":"longitude"}).attrs['content'])
                store_name.append(name)
                tem_var.append(street_address + ' ' + street_address1)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append(hours + ' '+time)
                tem_var.append("https://locator.chase.com/"+i['href'])
                store_detail.append(tem_var)
        else:
            r = requests.get("https://locator.chase.com/"+i['href'])
            soup1= BeautifulSoup(r.text,"lxml")
            link = soup1.find_all("a",{"class":"Directory-listLink"})
            if len(link) != 0:
                for j in link:
                    
                    street_address1=''
                    data_count = j.attrs['data-count'].replace("(","").replace(")","")
                    if data_count == "1":
                        tem_var =[]
                        new_link =  "https://locator.chase.com/"+j['href'].replace("..","")
                        r = requests.get(new_link)
                        soup2= BeautifulSoup(r.text,"lxml")
                        latitude = (soup2.find("meta",{"itemprop":"latitude"}).attrs['content'])
                        longitude = (soup2.find("meta",{"itemprop":"longitude"}).attrs['content'])
                        name = (soup2.find("h1",{"class":"Core-title"}).text)
                        street_address = soup2.find("span",{"class":"c-address-street-1"}).text
                        street_address2 = soup2.find("span",{"class":"c-address-street-2"})
                        if street_address2 != None:
                            street_address1 = street_address2.text
                        city = soup2.find("span",{"class":"c-address-city"}).text
                        state1 =  soup2.find("abbr",{"class":"c-address-state"})
                        if state1 != None:
                            state = state1.text
                        else:
                            state = "<MISSING>"
                        zip1 = soup2.find("span",{"class":"c-address-postal-code"}).text
                        phone = soup2.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                        hours1 = soup2.find("table",{"class":"c-hours-details"})
                        time1 = soup2.find("div",{"class":"Core-hoursToday"})
                    
                        hours =''
                        time=''
                        if time1 != None:
                            time ="ATM" +' '+ (" ".join(list(time1.stripped_strings)).replace("Day of the Week Hours",""))
                        if hours1 != None:
                            hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))
            
                        store_name.append(name )
                        tem_var.append(street_address + ' ' + street_address1)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append("US")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone)
                        tem_var.append("<MISSING>")
                        tem_var.append(latitude)
                        tem_var.append(longitude)
                        tem_var.append(hours +' '+ time)
                        tem_var.append("https://locator.chase.com/"+j['href'].replace("..",""))
                        store_detail.append(tem_var)
                        print(tem_var)
                    else:
                        new_link =  "https://locator.chase.com/"+j['href'].replace("..","")
                        r = requests.get(new_link)
                        soup4= BeautifulSoup(r.text,"lxml")
                        link2 = soup4.find_all("a",{"class":"Teaser-titleLink"})
                        for j in link2:
                            tem_var=[]
                            street_address1=''
                            r = requests.get("https://locator.chase.com/"+j['href'].replace("..",""))
                            soup5= BeautifulSoup(r.text,"lxml")
                            name = (soup5.find("h1",{"class":"Core-title"}).text)
                            street_address = soup5.find("span",{"class":"c-address-street-1"}).text
                            street_address2 = soup5.find("span",{"class":"c-address-street-2"})
                            if street_address2 != None:
                                street_address1 = street_address2.text
                            city = soup5.find("span",{"class":"c-address-city"}).text
                            state1 =  soup5.find("abbr",{"class":"c-address-state"})
                            if state1 != None:
                                state = state1.text
                            else:
                                state = "<MISSING>"
                            zip1 = soup5.find("span",{"class":"c-address-postal-code"}).text
                            phone = soup5.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                            hours1 = soup5.find("table",{"class":"c-hours-details"})
                            hours =''
                            time=''
                            if time1 != None:
                                time ="ATM" +' '+ (" ".join(list(time1.stripped_strings)).replace("Day of the Week Hours",""))
                            if hours1 != None:
                                hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))

                            latitude = (soup5.find("meta",{"itemprop":"latitude"}).attrs['content'])
                            longitude = (soup5.find("meta",{"itemprop":"longitude"}).attrs['content'])
                            store_name.append(name )
                            tem_var.append(street_address + ' ' + street_address1)
                            tem_var.append(city)
                            tem_var.append(state)
                            tem_var.append(zip1)
                            tem_var.append("US")
                            tem_var.append("<MISSING>")
                            tem_var.append(phone)
                            tem_var.append("<MISSING>")
                            tem_var.append(latitude)
                            tem_var.append(longitude)
                            tem_var.append(hours + ' ' +time)
                            tem_var.append("https://locator.chase.com/"+j['href'].replace("..",""))
                            store_detail.append(tem_var)
                            print(tem_var)
            else:
                tem_var=[]
                street_address1=''
                r = requests.get("https://locator.chase.com/"+i['href'])
                soup6= BeautifulSoup(r.text,"lxml")
                name = (soup6.find("h1",{"class":"Core-title"}).text)
                street_address = soup6.find("span",{"class":"c-address-street-1"}).text
                street_address2 = soup6.find("span",{"class":"c-address-street-2"})
                if street_address2 != None:
                    street_address1 = street_address2.text
                city = soup6.find("span",{"class":"c-address-city"}).text
                state1 =  soup6.find("abbr",{"class":"c-address-state"})
                if state1 != None:
                    state = state1.text
                else:
                    state = "<MISSING>"
                zip1 = soup6.find("span",{"class":"c-address-postal-code"}).text
                phone = soup6.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                hours1 = soup6.find("table",{"class":"c-hours-details"})
                time1 = soup2.find("div",{"class":"Core-hoursToday"})
                hours =''
                time=''
                if time1 != None:
                    time ="ATM" +' '+ (" ".join(list(time1.stripped_strings)).replace("Day of the Week Hours",""))
                if hours1 != None:
                    hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))
                latitude = (soup2.find("meta",{"itemprop":"latitude"}).attrs['content'])
                longitude = (soup2.find("meta",{"itemprop":"longitude"}).attrs['content'])
                store_name.append(name)
                tem_var.append(street_address + ' ' + street_address1)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append(hours + ' '+time)
                tem_var.append("https://locator.chase.com/"+i['href'])
                store_detail.append(tem_var)
                print(tem_var)
        
    # print("======================",len(store_name)) 
    # print(len(store_detail))            
    for i in range(len(store_name)):
       store = list()
       store.append("https://locator.chase.com")
       store.append(store_name[i])
       store.extend(store_detail[i])
       if  store[2] in result:
           continue
       result.append(store[3])
       return_main_object.append(store)
      
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


