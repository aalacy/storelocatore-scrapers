import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re
import itertools


# Location URL
location_url = 'https://www.bandanasbbq.com/list-of-locations'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'



# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_hours(content):
    hours = '; '.join([x.text.strip() for x in content.find_all('div', {'class':'col-sm-3 col-sm-push-1 footer-info'})[0].find_all('p') if 'pm' in x.text])
    return hours


def pull_info(content):

    # list of lists of stores
    location_data = [x.find_all('li') for x in content.find_all('div',{'class':'col-sm-4'})]

    # flatten the lists
    location_data = list(itertools.chain(*location_data))

    store_data = []

    # Pull hours - same for all stores
    hours = pull_hours(content)

    for store in location_data:

        store_name = "Bandana's Bar-B-Q " + store.h3.text.split(', ')[0]

        store_type = '<MISSING>'

        # Split up address tag to parse
        address_split = store.p.text.replace('\n\t\t\t\t\t\t\t\t\t','\n').split('\n')

        # determine which piece of list state and city listed. Always one before phone number
        state_city_line = [(id, x) for id, x in enumerate(address_split,0) if 'Phone Number' in x][0][0] - 1

        city = address_split[state_city_line].replace('Lebanon MO ','Lebanon, ').split(', ')[0]

        state = re.findall(' ([A-Za-z]{2}) ', address_split[state_city_line].replace('Indiana','IN'))[0].upper()

        zip = re.search('\d{4,6}', address_split[state_city_line]).group(0)

        # Always comes line after state/zip
        phone = ''.join([x for x in address_split[state_city_line+1] if x.isnumeric()])

        # Concatenate all parts of list prior to city state for street address
        street_add = ' '.join([x for x in address_split[0:state_city_line] if x != ''])

        try:
            raw_lat_long = pull_content(store.a['href']).iframe['src']
            long = re.search('!2d(.*)!3d', raw_lat_long).group(0).replace('!2d', '').replace('!3d', '')
            lat = re.search('!3d(.*)!3m2!', raw_lat_long).group(0).replace('!3d', '')[:7]
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

soup = pull_content(location_url)



# Pull all stores and info

final_df = pull_info(soup)



# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)
