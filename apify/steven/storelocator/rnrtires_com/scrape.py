import pandas as pd
import requests as r
import os
import re


# Javascript location of all information
location_url = 'http://www.rnrtires.com/rnr-locations/'
# php store info dump
store_data_url = 'https://www.rnrtires.com/wp-admin/admin-ajax.php?action=store_search&lat=29.2108147&lng=-81.02283310000001&max_results=1000&search_radius=50&autoload=1'


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
    soup = r.get(url,headers=header).json()

    return soup


def pull_info(content):

    # list of store hrefs
    stores = content

    store_data = []

    for store in stores:
        if ';' in store['store']:
            store_name = store['store'].split(';')[1].strip()
        elif ' – ' in store['store']:
            store_name = store['store'].split(' – ')[1].strip()
        else:
            store_name = store['store']

        store_number = store['id']
        store_type = '<MISSING>'
        street_add = (store['address'] + ' ' + store['address2']).strip()
        city = store['city']
        state = store['state']
        country_cd = 'US' if store['country']=='United States' else 'FIX'
        zip = store['zip']
        phone = ''.join([x for x in store['phone'] if x.isnumeric()])
        phone = '<MISSING>' if phone=='' else phone
        hours = re.sub('  </tr>',' ',re.sub('</time>','; ',re.sub('</td>',' ',re.sub('<time>','',re.sub('<[a-z]{2}>','',store['hours']))))).replace(' </tr></table>','').split('>')[1]
        lat = store['lat']
        long = store['lng']

        temp_data = [

            location_url,

            store_name,

            street_add,

            city,

            state,

            zip,

            country_cd,

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

        'hours_of_operation']



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df



# Pull URL Content

content = pull_content(store_data_url)

# Pull all stores and info

final_df = pull_info(content)


# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)