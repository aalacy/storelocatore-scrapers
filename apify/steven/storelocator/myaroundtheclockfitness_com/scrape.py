import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'http://myaroundtheclockfitness.com/gyms/'

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
    store_hrefs = [x['href'] for x in content.find_all('a',{'class':'btn fcs-btn'}) if 'virtualtour' not in x['href']]

    store_data = []

    for href in store_hrefs:

        store = pull_content(href)

        address_split = store.find_all('div', {'class': 'fusion-text'})[1].text.split('\n')

        state_city_line = [(id, x) for id, x in enumerate(address_split) if re.search('[A-Z]{2} (\d{5,6})', x.replace(',',''))][0][0]

        store_name = store.h1.text

        store_type = '<MISSING>'

        # extract address and remove trailing commas
        street_add = ' '.join([x for x in address_split[0:state_city_line] if x != ''])
        street_add = street_add[:-1] if street_add[-1:] == ',' else street_add

        city = address_split[state_city_line].split(', ')[0]

        state = re.findall(' ([A-Za-z]{2}) ', address_split[state_city_line].replace(',',' '))[0].upper()

        zip = re.search('\d{4,6}', address_split[state_city_line]).group(0)

        # Always comes line after state/zip
        phone = ''.join([x for x in address_split[state_city_line+1] if x.isnumeric()])

        # hours
        hours = 'Monday - Sunday: 12AM - 12 PM'

        # Location data missing
        # "latitude":"26.4929194","longitude":"-81.84976410000002"

        try:
            raw_lat_long = str(store.find_all('section',{'id':'content'}))
            raw_lat_long = re.search('"latitude":".*","longitude":".*"',raw_lat_long).group(0).split(',')
            lat = raw_lat_long[0].split('"')[3]
            long = raw_lat_long[1].split('"')[3]
        except:
            lat = '<MISSING>'
            long = '<MISSING>'


        temp_data = [

            href,

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


