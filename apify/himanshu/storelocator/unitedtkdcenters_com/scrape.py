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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://unitedtkdcenters.com/locations"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k = (soup.find_all("a",{"data-ux":"ContentCardButton"}))
    # names = (soup.find_all("h4",{"data-ux":"ContentCardHeading"}))
    # for j in names[:-6]:
    #     if j.text:
    #         store_name.append(j.text)
    phone =[]
    hours =[]
    for i in k[:-4]:
        tem_var =[]

        r = requests.get("https://unitedtkdcenters.com"+i['href'],headers=headers)
        soup1= BeautifulSoup(r.text,"lxml")

        if soup1.find("p",{"data-ux":"Text","data-aid":"CONTACT_INFO_ADDRESS_REND"}) !=None:

            v = soup1.find("p",{"data-ux":"Text","data-aid":"CONTACT_INFO_ADDRESS_REND"}).text.split(',')
            stopwords = " United States"
            new_words = [word for word in v if word not in stopwords]

            if len(new_words) ==2:
                street_address = new_words[0]
                city = new_words[1]

                tem_var.append(street_address)
                store_name.append(street_address)
                tem_var.append(city)
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                store_detail.append(tem_var)

            elif len(new_words) ==3:
                street_address = new_words[0]

                city = new_words[1]
                zipcode = (new_words[2].split( )[-1])
                state = " ".join(new_words[2].split( )[:-1])

                tem_var.append(street_address)
                store_name.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode.strip())
                store_detail.append(tem_var)

            elif len(new_words) ==4:
                street_address = new_words[0]
                city = new_words[1]

                words = [word.replace(' USA','NJ 07423') for word in new_words[2:]]
                zipcode = (words[-1].split( )[-1])
                state = " ".join(words[-1].split( )[:-1])

                tem_var.append(street_address)
                store_name.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode.strip())
                store_detail.append(tem_var)
                
        if soup1.find("a",{"data-ux":"Link","data-aid":"CONTACT_INFO_PHONE_REND"}) !=None:
            phone.append(soup1.find("a",{"data-ux":"Link","data-aid":"CONTACT_INFO_PHONE_REND"}).text)

        if soup1.find("table") !=None:
            hours.append(soup1.find("table").text)
 
   
    del store_name[-1]
    del store_detail[-1]
    for i in range(len(store_name)):
        store = list()
        store.append("https://unitedtkdcenters.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i])
        store.append("unitedtkdcenters")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours[i])
        return_main_object.append(store)
 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
