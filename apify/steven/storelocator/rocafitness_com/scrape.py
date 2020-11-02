import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'http://rocafitness.com/'

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
    store_hrefs = [location_url + '/' + x['href'] for x in content.find_all('a') if 'ROCA' in x.text]

    # empty list to house store data before turning to df
    store_data = []

    for href in store_hrefs:

        # pull store data
        store = pull_content(href)

        # store name
        store_name = re.sub(r'(\r|\n)','',store.h3.text).strip()

        # store type, either corporate or a fitness location
        store_type = 'Corporate Office' if 'Corporate' in store_name else 'Fitness Location'

        # split location data into a list
        add_raw = re.search('ADDRESS (.*)[A-Z]{2}(.*)\d{5}',re.sub('(<(.*)>|\r|\n|\s{1,30})',' ',str(store).replace('<br/>',','))).group(0).replace('ADDRESS','').split(',')
        add_raw = [x.strip() for x in add_raw if x.strip()!='']

        # parse based on the length of the list
        if len(add_raw)==3:
            street_add = add_raw[0]
            city = add_raw[1]
            state = add_raw[2][:2]
            zip = add_raw[2][3:]
        else:
            street_add = add_raw[0] + ' ' + add_raw[1]
            city = add_raw[2]
            state = add_raw[3][:2]
            zip = add_raw[3][3:]

        # phone
        phone = re.search('PHONE (.*)-[A-Z0-9]{4}',re.sub('(<(.*)>|\r|\n|\s{1,30})',' ',str(store))).group(0).replace('PHONE','').replace(' ','')

        # hours
        hours = re.search('HOURS OF OPERATION (.*) PM',re.sub('(<(.*)>|\r|\n|\s{1,30})',' ',str(store).replace('<br/>','; '))).group(0).replace('HOURS OF OPERATION','').replace(' ','')
        hours = hours[1:] if hours[:1] ==';' else hours
        hours = hours.replace(';','; ')

        # lat and long not in data
        lat = '<MISSING>'
        long = '<MISSING>'



        temp_data = [

            href,

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