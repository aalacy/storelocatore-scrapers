import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import time
import unicodedata
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    code = {}

    soup = bs(session.get("https://www.marriottvacationclub.com/vacation-resorts/").text, "lxml")

    for param in soup.find(lambda tag: (tag.name == "script") and 'resorts.push(' in tag.text).text.split("resorts.push(")[1:]:
        if param.split('region: "')[1].split('"')[0].strip() != "North America":
            continue
        page_url =  "https://www.marriottvacationclub.com/vacation-resorts/" + param.split('permalink: "')[1].split('"')[0]
        
        location_soup = bs(session.get(page_url + "/map/").text, "lxml")

        location_name = location_soup.find("span", {"itemprop":"name"}).text
        
        street_address = location_soup.find("span", {"itemprop":"name"}).text
        city = location_soup.find("span", {"itemprop":"addressLocality"}).text
        state = location_soup.find("span", {"itemprop":"addressRegion"}).text
        zipp = location_soup.find("span", {"itemprop":"postalCode"}).text
        phone = location_soup.find_all("a", {"class":"telephone-number"})[1].text
        country_code = location_soup.find("span", {"itemprop":"addressCountry"}).text
        location_type = "Marriott Vacation Club"
        coords = location_soup.find(lambda tag:(tag.name == "script") and "googleMap.attr('src',"  in tag.text).text.split("googleMap.attr('src',")[1].split(");")[0].replace('"',"").strip()
        lat = coords.split("!3d")[1].split("!2m")[0]
        lng = coords.split("!2d")[1].split("!3d")[0]
       

        store = []
        store.append("https://www.marriottvacationclub.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store

        # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    # }
    # for region in session.get("https://pacsys.marriott.com/data/marriott_properties_MC_en-US.json", headers=headers).json()['regions']:

    #     if region['region_id'] == "north.america":

    #         for country in region['region_countries']:

    #             if country['country_code'] == "US":
                    
    #                 for regions in  country['country_states']:

    #                     for city_name in regions['state_cities']:

    #                         for city_property in city_name['city_properties']:

    #                             if city_property['brand_code'] == "MV":

    #                                 location_name = city_property['name']
    #                                 
    #                                 page_url = "https://www.marriottvacationclub.com/vacation-resorts/"+str(city_property['marsha_code'].lower())+"-"+str(code[city_property['marsha_code'].lower().replace("ctdst","ctdsr").replace("rnogr","rnoph")])
   

def scrape():
    data = fetch_data()
    write_output(data)

scrape()