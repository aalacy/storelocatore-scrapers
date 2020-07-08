import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    
    url = 'https://lightshade.com/wp-admin/admin-ajax.php'
    params = (
            ('action', 'asl_load_stores'),
            ('nonce', '97453abb26'),
            ('load_all', '1'),
            ('layout', '1'),
        )
    r = session.get(url, headers=headers, params=params,verify=False)
    stores = r.json()
    p = 0
    #print(stores)
    for store in stores:
        link = store['website']
        title = store['title']
        sid = store['id']
        ltype = 'Store'       
        street = store['street']
        city = store['city']
        pcode = store['postal_code']        
        state = store['state']      
        phone = store['phone']      
        lat = store['lat']      
        longt = store['lng']
        hours = 'Sunday ' + store['start_time_0']+ '-'+ store['end_time_0']+  ' Monday ' + store['start_time_1']+ '-' + store['end_time_1'] + ' Tueday ' + store['start_time_2']+ '-'+ store['end_time_2']+  ' Wednesday ' + store['start_time_3']+ '-'+ store['end_time_3']+ ' Thursday ' + store['start_time_4']+ '-'+ store['end_time_4']+  ' Friday ' + store['start_time_5']+ ' - '+ store['end_time_5'] + ' Saturday ' + store['start_time_6']+ '-'+ store['end_time_6']
        hours = hours.replace('-',' - ')
        #hours = f"Daily Start time:{store['start_time_0']} Daily End time: {store['end_time_0']}"
        ccode = store['country']
        if ccode == 'United States':
            ccode = 'US'
        data.append(['https://lightshade.com/', link, title, street, city, state, pcode, 'US', sid, phone, ltype, lat, longt, hours])
        #print(p,data[p])
        p += 1

 
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
