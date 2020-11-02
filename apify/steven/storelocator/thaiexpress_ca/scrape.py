import pandas as pd
import requests as r
import os
from bs4 import BeautifulSoup as bs
import re

#TODO: Update requirements file and all dependency files.
#TODO: Ask how to handle preview vs open facilities

# Location URL
location_url = 'https://thaiexpress.ca/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1564582064002'

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
    soup = bs(r.get(url,headers=header).content,'lxml')

    return soup

def pull_info(content):

    # list of store hrefs
    stores = content.find_all('item')

    store_data = []

    for store in stores:

        store_name = store.location.text

        store_type = '<MISSING>'

        store_number = '<MISSING>'

        add_raw = store.address.text

        street_add = '<INACCESSIBLE>'

        city = '<INACCESSIBLE>'

        state = '<INACCESSIBLE>'

        zip = '<INACCESSIBLE>'

        phone = ''.join([x for x in [x for x in store.address.find_next_siblings() if 'phone' in str(x)][0].text if x.isnumeric()])

        hours = re.sub('</div>|<div>|&nbsp|\r\n',' ',[x for x in store.address.find_next_siblings() if 'operatinghours' in str(x)][0].text).strip().replace(' - ',': ').replace('y:','y -')

        # some of them have unncessary words or characters, so this is an re-method to eliminate those
        hours = str([x for x in re.findall('(Monday to Sunday|'
                               'Monday|'
                               'Tuesday|'
                               'Wednesday|'
                               'Thursday|'
                               'Friday|'
                               'Saturday|'
                               'Sunday|'
                                'Closed|'
                                '\d{1,2}-\d{2}pm|'
                               '\d{1,2}-\d{2}pm|'
                                '\d{1,2}am:\d{2}pm|'
                               '\d{1,2}pm:\d{2}pm|'
                                '\d{1,2}:\d{2}am|'
                               '\d{1,2}:\d{2}pm|'
                               '\d{1,2}am|'
                               '\d{1,2}pm|'
                               '\d{1,2}:\d{2}|'
                               '\d{1,2}:\d{2}|'
                               '\d{1,2}-\d{2}|'
                               '\d{1,2}-\d{2}|'
                               ')',hours) if x != '']).replace('[','').replace(']','').replace("'",'').replace('y,','y:')

        # Some don't have hours, so just say missing
        if 'Sunday: Monday: Tuesday: Wednesday: Thursday: Friday: Saturday' in hours:
            hours = '<MISSING>'
        if 'Monday: Tuesday: Wednesday: Thursday: Friday: Saturday: Sunday' in hours:
            hours = '<MISSING>'

        lat = [x for x in store.address.find_next_siblings() if 'latitude' in str(x)][0].text

        long = [x for x in store.address.find_next_siblings() if 'longitude' in str(x)][0].text



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

            hours,

            add_raw
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

        'raw_address'

        ]



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df





# Pull URL Content
content = pull_content(location_url)

# Pull all stores and info
final_df = pull_info(content)

# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)
