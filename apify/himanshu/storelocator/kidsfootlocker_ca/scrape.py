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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://stores.footlocker.ca"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    result =[]
    addresses=[]
    k= soup.find_all("a",{"class":"Directory-listLink"})

    for i in k:
        r = session.get("https://stores.footlocker.ca/"+i['href'])
        print("============",i.text)
        soup1= BeautifulSoup(r.text,"lxml")
        link = soup1.find_all("a",{"class":"Directory-listLink"})

        if len(link) != 0:
            for j in link:
                tem_var =[]
                street_address1=''
                new_link =  "https://stores.footlocker.ca"+j['href'].replace("..","")
                data_count = j.attrs['data-count'].replace("(","").replace(")","")
                if data_count == "1":
                    # if "https://stores.kidsfootlocker.com/pr/pr/bayamon.html" in new_link:
                        # print("+++++++++++++++++++",new_link)
                    r = session.get(new_link)
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
                        state = "<MISSING>"
                    zip1 = soup2.find("span",{"class":"c-address-postal-code"}).text
                    phone = soup2.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                    hours1 = soup2.find("table",{"class":"c-hours-details"})
                    if hours1 != None:
                        hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))
          
                    lat = soup2.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][0].split("&dro")[0]
                    lng = (soup2.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][1].split("&dro")[0])
                    # tem_var.append("https://stores.footlocker.ca")
                    store_name.append(name + ' ' +name1)
                    tem_var.append(street_address + ' ' + street_address1)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("CA")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(lat)
                    tem_var.append(lng)
                    tem_var.append(hours)
                    tem_var.append("https://stores.footlocker.ca"+j['href'].replace("..",""))
                    store_detail.append(tem_var)
                else:
                    r = session.get(new_link)
                    soup4= BeautifulSoup(r.text,"lxml")
                    link2 = soup4.find_all("a",{"class":"Teaser-titleLink"})
                    for j in link2:
                        tem_var=[]
                        street_address1=''
                        # print(j['href'].replace("..",""))
                        r = session.get("https://stores.footlocker.ca"+j['href'].replace("..",""))
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
                            state = "<MISSING>"
                        zip1 = soup5.find("span",{"class":"c-address-postal-code"}).text
                        phone = soup5.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                        hours1 = soup5.find("table",{"class":"c-hours-details"})
                        lat = soup5.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][0].split("&dro")[0]
                        lng = (soup5.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][1].split("&dro")[0])
                        if hours1 != None:
                            hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))

                        # tem_var.append("https://stores.footlocker.ca")
                        store_name.append(name + ' ' +name1)
                        tem_var.append(street_address + ' ' + street_address1)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append("CA")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone)
                        tem_var.append("<MISSING>")
                        tem_var.append(lat)
                        tem_var.append(lng)
                        tem_var.append(hours)
                        tem_var.append("https://stores.footlocker.ca"+j['href'].replace("..",""))

                        store_detail.append(tem_var)
                        # yield tem_var 
        else:
            tem_var=[]
            street_address1=''
            r = session.get("https://stores.footlocker.ca/"+i['href'])
            soup6= BeautifulSoup(r.text,"lxml")
            name = soup6.find("span",{"class":"LocationName-brand"}).text
            name1 = soup6.find("span",{"class":"LocationName-geo"}).text
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
            if hours1 != None:
                hours = (" ".join(list(hours1.stripped_strings)).replace("Day of the Week Hours",""))
    
            lat = soup6.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][0].split("&dro")[0]
            lng = (soup6.find("a",{"class":"c-uber-ride-link is-uber-unwrapped"})['href'].split("5D=")[-3:][1].split("&dro")[0])
            # tem_var.append("https://stores.footlocker.ca")
            store_name.append(name + ' ' +name1)
            tem_var.append(street_address + ' ' + street_address1)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("CA")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(lat)
            tem_var.append(lng)
            tem_var.append(hours)
            tem_var.append("https://stores.footlocker.ca"+i['href'])
            store_detail.append(tem_var)

    # print("======================",len(store_name)) 
    # print(len(store_detail))            
    for i in range(len(store_name)):
       store = list()
       store.append("https://stores.footlocker.ca")
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


