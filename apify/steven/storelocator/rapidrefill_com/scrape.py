import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://rapidrefill.com/'

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
    stores = [x for x in content.find_all('div',{'class':'et_pb_text_inner'}) if 'HOURS' in str(x)]

    # empty list to house store data before turning to df
    store_data = []

    for store in stores:

        # list of all store info
        store_list = store.h3.find_next_siblings()

        # store name
        store_name = re.search('<strong>(.*)</strong>', str(store_list[1])).group(0).replace('<strong>', '').replace('</strong>',
                                                                                                        '').title()
        # store type
        store_type = '<MISSING>'

        # location info
        street_add = re.sub('<br/>','',re.search('<br/> (.*)<br/>',str(store_list[1])).group(0)).strip()
        # used to parse city state and zip
        add_raw = re.search('<br/> [A-Za-z]{2,50}, [A-Z]{2} \d{4,5}</p>',str(store_list[1])).group(0).replace('<br/>','').replace('</p>','').strip()
        city = add_raw.split(',')[0]
        state = re.search('[A-Z]{2}',add_raw).group(0)
        zip = re.search('\d{4,5}',add_raw).group(0)

        # phone
        phone = ''.join([x for x in store_list[0].text if x.isnumeric()])

        # hours
        hours = store_list[2].text.replace('\xa0','').replace('HOURS ','')

        # lat and long not in data
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