import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://www.ride-indoorcycling.com/studios/'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_info(content):

    # list of store hrefs
    stores = content.find_all('div',{'class':'info'})

    store_data = []

    for store in stores:

        store_name = store.h5.text.strip()

        store_type = '<MISSING>'

        try:
            street_add = store.a.text.strip().split(',')[0]
            city = store.a.text.strip().split(',')[1].strip().title()
            state = store.a.text.strip().split(',')[2].strip().split(' ')[0]
            zip = store.a.text.strip().split(',')[2].strip().split(' ')[1]
        except:
            # One of the entries is missing a comma, so add it in
            street_add_raw = store.a.text.replace('Houston,',',Houston,')
            street_add = street_add_raw.split(',')[0].strip()
            city = street_add_raw.strip().split(',')[1].strip().title()
            state = street_add_raw.strip().split(',')[2].strip().split(' ')[0]
            zip = street_add_raw.strip().split(',')[2].strip().split(' ')[1]

        # Always comes line after state/zip
        phone = ''.join([x for x in store.find('a',{'class':'locTel'}).text if x.isnumeric()])

        # hours
        hours = ''
        hours = hours if 'PM' in hours else '<MISSING>'

        # lat long url to parse
        lat = '<MISSING>'
        long = '<MISSING>'


        temp_data = [

            location_url,

            store_name,

            street_add,

            city,

            state,

            zip,

            'US',

            '<MISSING>',

            phone,

            store_type,

            lat,

            long,

            hours

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

        'hours_of_operation']



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df



# Pull URL Content

content = pull_content(location_url)

# Pull all stores and info

final_df = pull_info(content)


# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)