import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'http://roadrunnermarkets.com/#locations'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content

def pull_content(url):
    # Website requires this to grant access
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    soup = bs(r.get(url,headers=header).content,'html.parser')

    return soup

def pull_info(content):

    # list of store hrefs
    stores = content.find_all('div',{'class':'location'})

    store_data = []

    for store in stores:

        store_name = 'Roadrunner Markets - ' + store.div.text

        store_type = '<MISSING>'

        store_number = store['data-location']

        street_add = store.div.text

        city = store.div.find_next().text.split(',')[0]

        state = store.div.find_next().text.split(',')[1].strip()

        # ZIP appears to be listed in the map, but cannot extract
        zip = '<INACCESSIBLE>'

        phone = ''.join([x for x in store.div.find_next().find_next().text if x.isnumeric()])

        hours = '<MISSING>'

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

            store_number,

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