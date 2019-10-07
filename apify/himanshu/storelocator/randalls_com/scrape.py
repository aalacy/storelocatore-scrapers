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
    base_url= "https://local.randalls.com/tx.html"
    base_url1 = "https://local.randalls.com/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    addresss =[]
    k= soup.find("div",{"class":"c-directory-list-content-wrapper"}).find_all("li")
    for i in k:
        r = requests.get(base_url1+i.a['href'])
        soup1= BeautifulSoup(r.text,"lxml")
        for j in (soup1.find_all("a",{"class":"Teaser-nameLink"})):
            tem_var = []
            r = requests.get(base_url1+j['href'].replace("..",""))
            link = base_url1+j['href'].replace("..","")
            soup2= BeautifulSoup(r.text,"lxml")
            street_address  = soup2.find("span",{"class":"c-address-street-1"}).text
            city = soup2.find("span",{"class":"c-address-city"}).text
            zipp =soup2.find("span",{"class":"c-address-postal-code"}).text
            state = soup2.find("abbr",{"class":"c-address-state"}).text
            name = soup2.find("span",{"class":"LocationName-geo"}).text
            phone = soup2.find("span",{"class":"c-phone-number-span c-phone-main-number-span"}).text
            json1 = soup2.find_all("div",{'class':"js-PharmacyData"})[-2].attrs['data-pharmacy-id']
            r = requests.get("https://local.randalls.com/pharmacydata/"+json1.replace("P","p")+".json").json()
            latitude = (json.loads(soup2.find("script",{"id":"js-map-config-dir-map-desktop"}).text)['locs'][0]['latitude'])
            longitude = (json.loads(soup2.find("script",{"id":"js-map-config-dir-map-desktop"}).text)['locs'][0]['longitude'])
            time = r['hours']['days']
            hours1 = ''
            hours2 =''
            for j in time:
                word = str(j['intervals'][0]['start'])
                index = 2
                char = ':'
                word = word[:index] + char + word[index + 1:]+"00"
                word1 = str(j['intervals'][0]['end'])
                index = 2
                char = ':'
                word1 = word1[:index] + char + word1[index + 1:]+"00"
                hours1 = hours1 +' '+ j['day'] + ' ' +word + ' '+word1
            hours2 = "Store Hours" + (" ".join(list(soup2.find("div",{"class":"c-location-hours-details-wrapper js-location-hours"}).stripped_strings)).replace("Day of the Week Date Hours",""))
            
    
            tem_var.append("https://local.randalls.com")
            tem_var.append(name)
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipp)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hours1 + ' '+hours2)
            tem_var.append(link)
            if tem_var[2] in addresss:
                continue
            addresss.append(tem_var[2])

            print(tem_var)
            yield tem_var
    


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


