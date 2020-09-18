import time
import csv
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain",'page_url', "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():  
    data=[]
    url = 'https://api.freshop.com/1/stores?app_key=breaux_mart&has_address=true&limit=-1&token=c9de29dbcae8efaea902e85213fd35b3'
    stores = session.get(url, headers=headers, verify=False).json()['items']
   
    print(len(stores))
    for i in range(len(stores)):
        location_name = stores[i]['name']
        street_address = stores[i]['address_1']
        city = stores[i]['city']
        state = stores[i]['state']
        zipcode = stores[i]['postal_code']
        phone = stores[i]['phone_md'].split('\n')[0]
        hours_of_op = stores[i]['hours_md']
        store_number = stores[i]['store_number']
        latitude = stores[i]['latitude']
        longitude = stores[i]['longitude']
        data.append([
             'https://www.breauxmart.com/',
             'https://www.breauxmart.com/my-store/store-locator',
              location_name,
              street_address,
              city,
              state,
              zipcode,
              'US',
              store_number,
              phone,
              '<MISSING>',
              latitude,
              longitude,
              hours_of_op.replace('\n',' ')
            ])
        #print(data[i])

    #time.sleep(3)
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
