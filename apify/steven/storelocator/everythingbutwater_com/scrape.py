import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://www.everythingbutwater.com/company/stores'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_info(content):

    # list of stores
    stores = [x for x in content.find_all('div',{'class':'row'}) if x.find_all('p',{'class':'location-name'})]

    store_data = []

    for store in stores:

        store_name = store.p.text.split('(')[0].strip()

        store_type = '<MISSING>'

        add_split = [re.sub('<([a-z]{1}|/[a-z]{1})>','',str(x)) for x in store.p.next_siblings if x != '\n']

        street_add = add_split[0]

        city = add_split[1].split(',')[0]

        state = re.search('[A-Z]{2}',add_split[1]).group(0)

        zip = re.search('\d{5}',add_split[1]).group(0)

        hours_phone_split = [x.text for x in store.find_all('p',{'class':'phone-hours'})]

        # Always comes line after state/zip
        phone = ''.join([x for x in hours_phone_split[0] if x.isnumeric()])

        # hours
        hours = hours_phone_split[1]
        hours = '<MISSING>' if '' else hours

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

soup = pull_content(location_url)

# Pull all stores and info

final_df = pull_info(soup).drop_duplicates()



# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)