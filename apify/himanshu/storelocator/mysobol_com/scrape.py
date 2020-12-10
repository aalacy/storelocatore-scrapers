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
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    get_url= "https://mysobol.com/wp-admin/admin-ajax.php?page=1&sortBy=id&sortDir=asc&perpage=0&with_schema=true&action=mapsvg_data_get_all&map_id=2365&table=database"
    # tmp_url = 'https://locations.53.com/'
    domain_url ='https://mysobol.com/'
    
    return_main_object=[]
    r = session.get(get_url,headers=headers).json()
    main = r['objects']
    for i in main:
        store =[]
        
        location_name = i['title']
        address = i['location']['address']['formatted'].split(',')[0]
        city = i['location']['address']['formatted'].split(',')[1]
        state = i['location']['address']['administrative_area_level_1_short']
        zip = i['location']['address']['postal_code']
        country_code = i['location']['address']['country_short']
        store_number = i['id']
        phone= i['phone'].replace('Location orders only','<MISSING>').strip()
        lat = i['location']['lat']
        lng = i['location']['lng']
        hour = i['hours']
        
      
    
        store.append(domain_url)                 
        store.append(location_name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append('<MISSING>')
        store.append(lat)
        store.append(lng)
        store.append(hour )
        store.append(get_url)
        return_main_object.append(store)

      
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
