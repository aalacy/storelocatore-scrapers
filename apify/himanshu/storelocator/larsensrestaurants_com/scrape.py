import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', 'w')as output_file:
        writer = csv.writer(output_file, delimiter=',')
        # header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # body
        for row in data or []:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    hour_append = []
    link_append=[]
    get_url = "https://www.larsensrestaurants.com/locations-and-menus"
    base_url = "https://larsensrestaurants.com/"
    
    r = requests.get(get_url, headers=headers)    
    soup = BeautifulSoup(r.text, "lxml")
    main1 =soup.find_all("div",{"class":"link-wrap"})     
    for i in main1:
        
        link1 = base_url+i.find('a')['href']
        link = link1.replace("../","")  
        link_append.append(link)
        
        r1 = requests.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        main2 =soup1.find("div",{"id":"location"})
        hour = main2.find("div",{"class":"hours"}).text
        hour_append.append(hour)
    main =soup.find("script",{"class":"js-react-on-rails-component"}).text
    js = json.loads(main)
    
    obj = js['preloadQueries'][0]['data']['restaurant']['locations']
    for index,i in enumerate(obj):
  
        # return_main_object = []
        location_name=i['name']
        address =i['streetAddress']
        city= i['city']
        state=i['state']
        zip = i['postalCode']
        country_code = i['country']
        store_number=i['id']
        phone=i['phone']
        lat= i['lat']
        lng=i['lng']      
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(address if address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hour_append[index])
        store.append(link_append[index])        
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
