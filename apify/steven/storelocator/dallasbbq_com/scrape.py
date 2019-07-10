import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Location URL
location_url = 'https://www.dallasbbq.com/'

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
    store_hrefs = [x['href'] for x in content.ul.find_all('ul',{'class':'sub-menu dropdown-menu depth_0'})[0].find_all('a')]

    store_data = []

    for href in store_hrefs:

        store = pull_content(href)

        store_name = re.sub('(\r|\n|\t)','',str(store.title.text)).split(',')[0].split('|')[0].split(':')[0].strip()

        store_type = '<MISSING>'

        raw_address = re.sub('\d{3}(-|.)\d{3}(-|.)\d{4}','\n',store.find_all('div',{'class':'container'})[0].p.text).split('\n')[0].strip()

        phone = re.search('\d{3}(-|.)\d{3}(-|.)\d{4}',store.find_all('div',{'class':'container'})[0].p.text).group(0)
        phone = ''.join([x for x in phone if x.isnumeric()])

        # hours
        hours = re.search('Store Hours:(.*) MENU',store.find_all('div',{'class':'container'})[0].p.text).group(0).replace('Store Hours:','').replace('\xa0','').replace('MENU','').strip()
        hours = hours if 'pm' or 'am' in hours else '<MISSING>'

        lat = '<MISSING>'
        long = '<MISSING>'



        temp_data = [

            href,

            store_name,

            '<MISSING>',

            '<MISSING>',

            'NY',

            '<MISSING>',

            'US',

            '<MISSING>',

            phone,

            store_type,

            lat,

            long,

            hours,

            raw_address

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

        'raw_address']



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df



# Pull URL Content

content = pull_content(location_url)

# Pull all stores and info

final_df = pull_info(content)



# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)