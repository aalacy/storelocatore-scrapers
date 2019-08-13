import pandas as pd
import requests as r
import os
from bs4 import BeautifulSoup as bs
import re

#TODO: Update requirements file and all dependency files.
#TODO: Ask how to handle preview vs open facilities

# Location URL
location_url = 'https://www.corkyskitchenandbakery.com/pages/locations'

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
    soup = bs(r.get(url,headers=header).content,'html.parser')

    return soup

def pull_info(content):

    # list of store hrefs
    stores = [x for x in content.find_all('h3')]

    store_data = []

    for store in stores:

        store_name = store.text.split('\n')[0].replace('\xa0','')

        store_type = '<MISSING>'

        store_number = '<MISSING>'

        # len(store.text.split('\xa0'))

        street_add = store.text.split('\n')[1].strip()

        city = store.text.split('\n')[2].split(',')[0].strip()

        state = re.search('[A-Z]{2}',store.text.split('\n')[2]).group(0)

        zip = re.search('(\d{4,6})',store.text.split('\n')[2]).group(0)

        phone = ''.join([x for x in store.a['href'] if x.isnumeric()])

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