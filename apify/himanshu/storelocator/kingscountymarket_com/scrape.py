import pandas as pd
import requests as r
import os
from bs4 import BeautifulSoup as bs
import re
import json

# Location URL
location_url = 'https://api-2.freshop.com/1/stores?app_key=kings_county_market&has_address=true&limit=-1&token=5d0e16faa5c05ad6628c2c83b392b4f9'
base_url = 'https://www.kingscountymarket.com/'
# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))


# file name of CSV output
file_name = 'data.csv'


def pull_content(url):
    # Website requires this to grant access
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    soup = (r.get(url,headers=header)).json()

    return soup

def pull_info(content):

    # list of store hrefs
    

    store_data = []

    for store in content['items']:

        store_name = store['name']

        store_type = '<MISSING>'

        page_url = store['url']

        store_number = store['store_number']

        street_add = store['address_1']

        city = store['city']

        state = store['state']

        zipp = store['postal_code']

        phone = store['phone_md'].split("\n")[0].strip()
        
        hours = store['hours_md'].replace("\n",' ').strip()

        lat = store['latitude']

        lng = store['longitude']



        temp_data = [

            base_url,

            store_name,

            street_add,

            city,

            state,

            zipp,

            'US',

            store_number,

            phone,

            store_type,

            lat,

            lng,

            hours,

            page_url
        ]



        store_data = store_data + [temp_data]



    final_columns = [

        'locator_domain',

        'location_name',

        'street_address',

        'city',

        'state',

        'zip',

        'country_code',

        'store_number',

        'phone',

        'location_type',

        'latitude',

        'longitude',

        'hours_of_operation',

        'page_url'

        ]



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df





# Pull URL Content
content = pull_content(location_url)

# Pull all stores and info
final_df = pull_info(content)

# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)