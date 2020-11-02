import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://redlandsgrill.com/locations/'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content
def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_info(content):

    # list of store information
    stores = content.find_all('div',{'class':'location-details'})

    # empty list to house store data before turning to df
    store_data = []

    for store in stores:

        # list of all store info
        store_list = store.p.find_next_siblings()

        # store type
        store_type = '<MISSING>'

        # used to parse city state and zip
        add_raw = [x.strip() for x in store.a.text.replace('\n\t', '').replace('\t', '; ').split(';') if
                   'opens' not in x]

        # location info
        street_add = add_raw[0]
        city = add_raw[1].split(',')[0]
        state = add_raw[1].split(',')[1]
        zip = add_raw[2]
        
        # set store name = city
        store_name = city

        # phone
        phone = ''.join([x for x in re.search('\d{3}-\d{3}-\d{4}',str(store).replace('(','').replace(')','').replace(' ','-')).group(0) if x.isnumeric()])

        # hours
        hours = re.sub('; $','',store.find('div',{'class':'hours'}).text.replace('\nHours of Operation\n','').replace('\n','; '))

        try:
            raw_lat_long = store.a['href']
            lat_long_list = re.search('@(.*),', raw_lat_long).group(0).replace('@', '').split(',')
            lat = lat_long_list[0]
            long = lat_long_list[1]
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