# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import csv
from sgrequests import SgRequests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline= "",encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    locator_domain = "http://claimjumper.com/"
    r  = session.get("https://www.claimjumper.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for loc in soup.find_all("p",class_="locationsList"):
        add = list(loc.stripped_strings)
        street_address = add[1].strip()
        city = add[2].split(",")[0].strip().replace("Tualatin","Portland")
        location_name = add[0].strip()
        state = add[2].split(",")[1].split()[0].strip()
        zipp = add[2].split(",")[1].split()[-1].strip()
        country_code = "US"
        phone = add[-1].strip()
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        page_url = "https://www.claimjumper.com"+loc.find("a",class_="locationLink")["href"].strip()
        
        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        longitude=''
        latitude=''
        hours_of_operation=''
        try:
            location_id = soup1.find("div",{"id":"map"}).find("div",class_="mfcard mf_map_card")["location_id"].strip()
            card_id = soup1.find("div",{"id":"map"}).find("div",class_="mfcard mf_map_card")["card_id"]
            token = soup1.find(lambda tag: (tag.name == "script") and "loadWidgets" in tag.text).text.split("('")[1].split("')")[0]
            headers = {
                'Accept': '*/*',
                'token':str(token),
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
                }
            url = "https://partner-api.momentfeed.com/locations/cards?location_id="+str(location_id)+"&card_id=7"
            r2= session.get(url,headers=headers)
            soup2 = BeautifulSoup(r2.text,"lxml")
            hours_of_operation = " ".join(list(soup2.find("dl",{"itemprop":"openingHours"}).stripped_strings))
            latitude = soup1.find("span",{"id":"jsLat"}).text.strip()
            longitude = soup1.find("span",{"id":"jsLong"}).text.strip()
            
        except:
            try:
                hours_of_operation = " ".join(list(soup1.find("h5",class_="hoursHeader").parent.stripped_strings)).replace("hours","").strip()
            except:
                hours_of_operation= "<MISSING>"
            try:
                latitude = soup1.find("span",{"id":"jsLat"}).text.strip()
                longitude = soup1.find("span",{"id":"jsLong"}).text.strip()
            except:
                latitude = "<MISSING>"
                longitude= "<MISSING>"
     

        
        store = [locator_domain, location_name, street_address.replace("Opry Mills Mall, ",''), city, state, zipp, country_code,
        store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        

        store = [str(x).replace("–","-").encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
        
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
