import pandas as pd
import requests as r
import os
from bs4 import BeautifulSoup as bs
import re

#TODO: Add in hours

# Location URL
location_url = 'http://www.lapizzaloca.com/?hcs=locatoraid&hca=search%3asearch%2f%2fproduct%2f_product_%2flat%2f%2flng%2f%2flimit%2f1000'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


def pull_content(url):
    soup = r.get(url).json()
    return soup

def pull_info(content):

    store_data = []

    for store in content['results']:

        store_name = store['name']

        store_type = '<MISSING>'

        store_number = store['id']

        street_add = store['street1']

        city = store['city']

        state = store['state']

        zip = store['zip']

        phone = ''.join([x for x in bs(store['phone']).a.text if x.isnumeric()])

        hours_raw = bs(r.get(bs(store['misc1']).a['href']).content)
        try:
            hours1 = re.search('Monday – Thursday \d{1,2}(pm|am)-\d{1,2}(pm|am)',str(hours_raw)).group(0)
        except:
            hours1 = ''
        try:
            hours2 = re.search('Friday -Saturday \d{1,2}(pm|am)-\d{1,2}(pm|am)',str(hours_raw)).group(0)
        except:
            hours2 = ''
        try:
            hours3 = re.search('Sunday \d{1,2}(pm|am)-\d{1,2}(pm|am)',str(hours_raw)).group(0)
        except:
            hours3 = ''

        hours = hours1 + ' ' + hours2 + ' ' + hours3
        hours = '<MISSING>' if hours == '  ' else hours

        lat = store['latitude']

        long = store['longitude']



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

        'hours_of_operation'

        ]



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df





# Pull URL Content
content = pull_content(location_url)

# Pull all stores and info
final_df = pull_info(content)

# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)