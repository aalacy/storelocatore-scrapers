import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Javascript location of all information
location_url = 'https://rapidfiredpizza.com/locations'
# php store info dump (minus lat and long)
store_data_url = 'https://rapidfiredpizza.com/location-data/getlocations.php'
# php store lat and long dump (to be merged on)
lat_long_url = 'https://rapidfiredpizza.com/location-data/map-test.php'

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

# Pull out all lat and ong data into a dictionary
def pull_lat_long(url):
    data = pull_content(lat_long_url)
    dict = {}
    for row in data.find_all('marker'):
        name = row['name']
        lng = row['lng']
        lat = row['lat']
        dict[name] = [lat,lng]
    return dict

def pull_info(content,lat_long_dict):

    # list of store hrefs
    stores = content.find_all('div',{'class':'location-small col-sm-4'})

    store_data = []

    for store in stores:

        # Store Name (Clean up)
        store_name = store.a.text.replace('Now Open: ','').replace('Coming Soon: ', '')

        # Add a status column for ones that are soon opening
        store_status = 'Coming Soon' if 'Coming Soon' in store.a.text else 'Open'

        store_type = '<MISSING>'

        # 2 formats of the data - put it into list form for extraction
        try:
            raw_add = [x for x in store.p.a.find_next_siblings() if
                       (str(x)!='<br/>') &
                       (str(x)!='TBD')][0]
        except:
            raw_add = [x for x in store.p if
                       (str(x)!='<br/>') &
                       (str(x)!='TBD')][0]
        # Further clean up list for extraction
        raw_add = [x for x in raw_add.text.replace('\t','').split('\n') if (x!='')]

        street_add = raw_add[0]

        city = raw_add[1].split(',')[0]

        state = raw_add[1].split(',')[1].strip().split(' ')[0]

        zip = raw_add[1].split(',')[1].strip().split(' ')[1]

        # Always comes line after state/zip
        phone = ''.join([x for x in store.p.text.split('\n')[0] if x.isnumeric()])

        # hours (concatenate two strings together)
        hours = re.search('Sun-Thu: (.*)',str(store)).group(0).replace('<br/>','') + '; ' + re.search('Fri-Sat: (.*)',str(store)).group(0).replace('<br/>','')
        hours = hours if 'pm' in hours else '<MISSING>'
        try:
            # lat long url to parse
            lat = lat_long_dict[store_name][0]
            long = lat_long_dict[store_name][1]
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

            hours,

            store_status

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

        'store_status']



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df



# Pull URL Content

content = pull_content(store_data_url)

# Pull all stores and info

final_df = pull_info(content,pull_lat_long(lat_long_url))



# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)