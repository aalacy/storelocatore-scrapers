import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://backwoods.com/store-locations'

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
    store_hrefs = [x['href'] for x in soup.find_all('a',{'class':'action primary'})]

    store_data = []

    for href in store_hrefs:

        href_data = pull_content(href)

        store = href_data.find_all('div',{'class':'block-locations'})

        store_name = store[0].h1.text.replace('Backwoods','Backwoods ')

        store_type = '<MISSING>'

        street_add = str(store[1].h3).split('<br/>')[0].replace('<h3>','')

        city = str(store[1].h3).split('<br/>')[1].replace('</h3>','').split(',')[0]

        state = str(store[1].h3).split('<br/>')[1].replace('</h3>','').split(',')[1].strip().split(' ')[0]

        zip = str(store[1].h3).split('<br/>')[1].replace('</h3>','').split(',')[1].strip().split(' ')[1]

        # Always comes line after state/zip
        phone = ''.join([x for x in store[0].a.text if x.isnumeric()])

        # hours
        hours = store[len(store)-1].text.replace('\n\n',' ').replace('m\n','m; ').replace('\n','').replace('Store Hours ','')
        hours = hours if 'pm' in hours else '<MISSING>'

        # lat long url to parse
        try:
            raw_lat_long = href_data.find_all('div',{'class':'block-locations'})[1].iframe['src']
            long = re.search('!2d(.*)!3d', raw_lat_long).group(0).replace('!2d', '').replace('!3d', '')
            lat = re.search('!3d(.*)!3m2!', raw_lat_long).group(0).replace('!3d', '')[:7]
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

soup = pull_content(location_url)

# Pull all stores and info

final_df = pull_info(soup)



# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)