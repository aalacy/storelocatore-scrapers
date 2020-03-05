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
        location_type = i['__typename']
        page_url = "https://www.larsensrestaurants.com/"+str(i['slug'])+"-california"
        
        r1 = requests.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            hour = " ".join(list(soup1.find("div",{"class":"hours"}).stripped_strings)).replace("Join us for Happy Hour Daily* from 5:00 PM to 7:00 PM & Sunday 5:00 PM to Close","").replace("* Holidays excluded Feb 14, 15, Easter, Mother's Day, Father's Day, Thanksgiving, Dec 24, 25, 31","").replace("Join us for Happy Hour Mon-Fri* from 5:00 PM to 7:00 PM & Sunday 5:00 PM to Close","").replace("Happy Hour Daily* 5-7pm *Holidays excluded including 2/14 & 2/15, Easter, Mother's Day, Father's Day, Thanksgiving, 12/24,25,31","").replace("Daily* from 5:00 PM- 7:00 PM","").replace("Join us for Happy Hour","").replace("Join us for Happy Hour Daily* from 4:00 PM to Close","")
        except:
            hour = "Monday - Friday from 5:00 PM to Close Saturday & Sunday from 3:00 PM to Close"
        
 

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
        store.append(hour)
        store.append(page_url)  
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]      
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
