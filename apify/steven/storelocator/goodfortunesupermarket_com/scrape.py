import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Location URL
location_url = 'http://goodfortunesupermarket.com/desktop.php?page=0'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_store_type(store_name):
    store_type = 'Warehouse' if 'WAREHOUSE' in store_name.upper() else 'SuperMarket'
    store_type = 'Food Court' if 'FOOD COURT' in store_name.upper() else store_type
    store_type = 'Main Office' if 'MAIN OFFICE' in store_name.upper() else store_type

    return store_type

def pull_location_info(store_name,text_content):

    # Location data is a mess. Some consistency, but basically have to parse separately
    # For main and east coast warehouse do this
    if store_name in ('MAIN OFFICE','EAST COAST WAREHOUSE'):
        street_add = text_content.p.text
        city = text_content.find_all('p',{'class':'address-margin'})[0].text.split(',')[0].strip()
        state = re.search('([A-Z]{2})', text_content.find_all('p',{'class':'address-margin'})[0].text).group(0)
        zip = re.search('\d{5,6}', text_content.find_all('p',{'class':'address-margin'})[0].text).group(0)
    else:
        # providence store is all messed up
        print(text_content.p.text)
        if store_name == 'Providence':
            city = store_name
            street_add = re.search('(.*) %s' % city, text_content.p.text).group(0)[:-11]
        elif store_name == 'Main St. Food Court':
            street_add = text_content.p.text.split(',')[0]
            city = re.search('.* [A-Z]{2}', text_content.p.text.split(',')[1]).group(0)[:-3].strip()
        elif len(text_content.p.text.split(',')) == 2:
            street_add = re.search('.*, [A-Z]{2}', text_content.p.text).group(0)[:-4]
            city = store_name
        elif len(text_content.p.text.split(',')) == 3:
            street_add = text_content.p.text.split(',')[0].strip()
            city = text_content.p.text.split(',')[1].strip()

        state = re.search('([A-Z]{2})', text_content.p.text).group(0)
        zip = re.search('\d{5,6}', text_content.p.text).group(0)

    return city, street_add, state, zip

def pull_info(content):

    store_data = []

    #################################
    # First handle corporate office #
    #################################

    store_name = content.find_all('h1', {'class': 'title title-main'})[0].text
    # determine store type
    store_type = pull_store_type(store_name)
    # pull raw info
    store = content.find_all('h1', {'class': 'title title-main'})[0].find_next_siblings()[0]
    #location info
    city, street_add, state, zip = pull_location_info(store_name, store)
    phone = store.find_all('p',{'class':'phone'})[0].a['href'].replace('tel:','')
    lat = '<MISSING>'
    long = '<MISSING>'
    hours = '<MISSING>'
    temp_data = [

        location_url,

        store_name.title(),

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

    ###############################
    # Handle East Coast Warehouse #
    ###############################

    store_name = content.find_all('h1',{'class':'title title-east'})[0].text
    # determine store type
    store_type = pull_store_type(store_name)
    # pull raw info
    store = content.find_all('h1',{'class':'title title-east'})[0].find_next_siblings()[0]
    # location info
    city, street_add, state, zip = pull_location_info(store_name, store)
    phone = store.find_all('p', {'class': 'phone'})[0].a['href'].replace('tel:', '')
    lat = '<MISSING>'
    long = '<MISSING>'
    hours = '<MISSING>'
    temp_data = [

        location_url,

        store_name.title(),

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

    # list of stores
    stores = content.find_all('div',{'class':'enlarge card'})

    for store in stores:

        store_name = store.h2.text

        # determine store type
        store_type = pull_store_type(store_name)

        # pull address info
        city, street_add, state, zip = pull_location_info(store_name,store)

        # Always comes line after state/zip
        phone = str(store.p.find_next_siblings()).replace('\n','').replace('\t','').replace('(','').replace(')','')
        phone = re.search('Phone: \d{3} \d{3}-\d{4}',phone).group(0)
        phone = ''.join([x for x in phone if x.isnumeric()])

        # hours
        hours = '<MISSING>'
        # lat long url to parse
        try:
            raw_lat_long = store.p.a['href']
            raw_lat_long = re.search('@(.*),', raw_lat_long).group(0).replace('@', '').split(',')
            lat = raw_lat_long[0]
            long = raw_lat_long[1]
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