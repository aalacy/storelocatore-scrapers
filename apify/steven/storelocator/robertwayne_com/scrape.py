import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://www.robertwayne.com/pages/locations'

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
    stores = [x for x in content.find_all('div',{'class':'Faq__Answer Rte'}) if 'Address:' in str(x)]

    store_data = []

    for store in stores:

        store_name = store.h3.text

        store_type = '<MISSING>'

        store_number = '<MISSING>'

        add_raw = [x.strip() for x in
                   store.p.find_next_sibling().find_next_sibling().text.replace('Address: ', '').split(',')]

        # Pull address and city based off list length
        if len(add_raw)==4:
            street_add = add_raw[0] + ' ' + add_raw[1]
            city = add_raw[2]
        elif len(add_raw)==3:
            street_add = add_raw[0]
            city = add_raw[1]
        else:
            try:
                # All the issue ones appear to be after <#\d{1,3}>, so try and strip all those out
                # If new ones appear in future without that format, then wont be included
                city = re.sub('#\d{1,10}', '', re.search('#\d{1,10} (.*)', add_raw[0]).group(0)).strip()
                street_add = add_raw[0][:-len(city)].strip()
            except:
                street_add = '<INACCESSIBLE>'
                city = '<INACCESSIBLE>'


        state = re.search('[A-Z]{2} ',store.p.find_next_sibling().find_next_sibling().text).group(0).strip()
        
        zip = re.search('[A-Z]{2} (\d{4,6})',store.p.find_next_sibling().find_next_sibling().text).group(0).strip()[3:]

        phone = ''.join([x for x in store.p.text if x.isnumeric()])

        hours = store.p.find_next_sibling().text.replace('Hours: ','')

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