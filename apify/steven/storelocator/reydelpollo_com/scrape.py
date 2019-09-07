import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://reydelpollo.com/locations/'

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
    stores = [x for x in content.find_all('div',{'class':'vc_row wpb_row vc_inner vc_row-fluid'}) if x.h4]

    store_data = []

    for store in stores:

        store_name = store.h4.text.split('(')[0].strip()

        store_type = '<MISSING>'

        street_add = store.h4.text.split('\n')[1].split(',')[0]

        city = store.h4.text.split('\n')[1].split(',')[1].strip()

        state = store.h4.text.split('\n')[1].split(',')[2].strip().split(' ')[0]

        zip = store.h4.text.split('\n')[1].split(',')[2].strip().split(' ')[1]

        # Always comes line after state/zip
        phone = ''.join([x for x in store.a['href'] if x.isnumeric()])

        # hours
        hours = [re.sub('\n','; ',re.sub('<.*>','',str(x))) for x in store.find_all('p') if 'Hours' in x.text][0][2:]
        hours = hours if 'PM' in hours else '<MISSING>'

        # lat long url to parse
        try:
            raw_lat_long = store.iframe['src']
            long = re.search('!2d(.*)!3d', raw_lat_long).group(0).replace('!2d', '').replace('!3d', '')
            lat = re.search('!3d(.*)!3m2!', raw_lat_long).group(0).replace('!3d', '')[:7]
        except:
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