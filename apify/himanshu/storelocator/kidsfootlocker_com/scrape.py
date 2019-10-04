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
    base_url= "https://stores.kidsfootlocker.com/index.html"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    addresss =[]

    k= soup.find_all("a",{"class":"Directory-listLink"})
   
    for i in k:
        r = requests.get("https://stores.kidsfootlocker.com/"+i['href'])
        print("============",i.text)
        soup1= BeautifulSoup(r.text,"lxml")

        link = soup1.find_all("a",{"class":"Directory-listLink"})
        
        
        street_address1=''
        if len(link) != 0:
            for j in link:
                tem_var =[]
                new_link =  "https://stores.kidsfootlocker.com"+j['href'].replace("..","")
                data_count = j.attrs['data-count'].replace("(","").replace(")","")
                if data_count == "1":
                    # if "https://stores.kidsfootlocker.com/pr/pr/bayamon.html" in new_link:
                        # print("+++++++++++++++++++",new_link)
                    r = requests.get(new_link)
                    soup2= BeautifulSoup(r.text,"lxml")
                    name = soup2.find("span",{"class":"LocationName-brand"}).text
                    name1 = soup2.find("span",{"class":"LocationName-geo"}).text
                    street_address = soup2.find("span",{"class":"c-address-street-1"}).text
                    street_address2 = soup2.find("span",{"class":"c-address-street-2"})
                    if street_address2 != None:
                        street_address1 = street_address2.text
                    city = soup2.find("span",{"class":"c-address-city"}).text
                    state1 =  soup2.find("abbr",{"class":"c-address-state"})
                    if state1 != None:
                        state = state1.text
                    else:
                        state = "PR"
                    zip1 = soup2.find("span",{"class":"c-address-postal-code"}).text
                    phone = soup2.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                    hours1 = soup2.find("table",{"class":"c-hours-details"})
                    if hours1 != None:
                        hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))
          
                    lat = soup2.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][0].split("&dro")[0]
                    lng = (soup2.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][1].split("&dro")[0])
                    # tem_var.append("https://stores.kidsfootlocker.com")
                    store_name.append(name + ' ' +name1)
                    tem_var.append(street_address + ' ' + street_address1)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(lat)
                    tem_var.append(lng)
                    tem_var.append(hours)
                    tem_var.append("https://stores.kidsfootlocker.com"+j['href'].replace("..",""))
                    store_detail.append(tem_var)
                else:
                    # print(new_link)
                    r = requests.get(new_link)
                    soup3= BeautifulSoup(r.text,"lxml")
                    link2 = soup3.find_all("a",{"class":"Teaser-titleLink"})

                    for j in link2:
                        tem_var=[]
                        # print(j['href'].replace("..",""))
                        r = requests.get("https://stores.kidsfootlocker.com"+j['href'].replace("..",""))
                        soup4= BeautifulSoup(r.text,"lxml")
                        name = soup4.find("span",{"class":"LocationName-brand"}).text
                        name1 = soup4.find("span",{"class":"LocationName-geo"}).text
                        street_address = soup4.find("span",{"class":"c-address-street-1"}).text
                        street_address2 = soup4.find("span",{"class":"c-address-street-2"})
                        if street_address2 != None:
                            street_address1 = street_address2.text
                        city = soup4.find("span",{"class":"c-address-city"}).text
                        state1 =  soup4.find("abbr",{"class":"c-address-state"})
                        if state1 != None:
                            state = state1.text
                        else:
                            state = "PR"
                        zip1 = soup4.find("span",{"class":"c-address-postal-code"}).text
                        phone = soup4.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                        hours1 = soup4.find("table",{"class":"c-hours-details"})
                        lat = soup4.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][0].split("&dro")[0]
                        lng = (soup4.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][1].split("&dro")[0])
                        if hours1 != None:
                            hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))

                        # tem_var.append("https://stores.kidsfootlocker.com")
                        store_name.append(name + ' ' +name1)
                        tem_var.append(street_address + ' ' + street_address1)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append("US")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone)
                        tem_var.append("<MISSING>")
                        tem_var.append(lat)
                        tem_var.append(lng)
                        tem_var.append(hours)
                        tem_var.append("https://stores.kidsfootlocker.com"+j['href'].replace("..",""))
                        # print("https://stores.kidsfootlocker.com"+j['href'].replace("..",""))
                        store_detail.append(tem_var)
                        
        else:
            tem_var=[]
            r = requests.get("https://stores.kidsfootlocker.com/"+i['href'])
            soup5= BeautifulSoup(r.text,"lxml")

          
            name = soup5.find("span",{"class":"LocationName-brand"}).text
            name1 = soup5.find("span",{"class":"LocationName-geo"}).text
            street_address = soup5.find("span",{"class":"c-address-street-1"}).text
            street_address2 = soup5.find("span",{"class":"c-address-street-2"})
            if street_address2 != None:
                street_address1 = street_address2.text
            city = soup5.find("span",{"class":"c-address-city"}).text
            state1 =  soup5.find("abbr",{"class":"c-address-state"})
            if state1 != None:
                state = state1.text
            else:
                state = "PR"
            zip1 = soup5.find("span",{"class":"c-address-postal-code"}).text
            phone = soup5.find("div",{"class":"Phone-display Phone-display--withLink"}).text
            hours1 = soup5.find("table",{"class":"c-hours-details"})
            if hours1 != None:
                hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))
    
            lat = soup5.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][0].split("&dro")[0]
            lng = (soup5.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][1].split("&dro")[0])
            # tem_var.append("https://stores.kidsfootlocker.com")
            store_name.append(name + ' ' +name1)
            tem_var.append(street_address + ' ' + street_address1)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(lat)
            tem_var.append(lng)
            tem_var.append(hours)
            tem_var.append("https://stores.kidsfootlocker.com"+i['href'])
            store_detail.append(tem_var)
            # print("=====",tem_var)

                
    for i in range(len(store_name)):
       store = list()
       store.append("https://stores.kidsfootlocker.com")
       store.append(store_name[i])
       store.extend(store_detail[i])
       if store[2] in addresss:
            continue
       addresss.append(store[2])
       return_main_object.append(store)
    return return_main_object
    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


