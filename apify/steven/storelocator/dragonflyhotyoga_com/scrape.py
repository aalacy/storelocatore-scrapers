import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re
import itertools

# Location URL
location_url = 'https://www.dragonflyhotyoga.com/'

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
    store_hrefs = [x.a['href'] for x in content.find_all('ul', {'class':'sub-menu sub-menu-1'})[0] if x != '\n']

    store_data = []

    for href in store_hrefs:

        href_data = pull_content(href)

        store_name = re.search('locations/(.*)/$',href).group(0).split('/')[1].replace('-wi','').replace('-',' ').title()

        store_type = '<MISSING>'

        location_raw = str(href_data.find_all('div',{'class':'contact-info'})[0]).replace('<div class="contact-info">','')

        street_add = re.sub('<[a-z]{1}>','',str(location_raw).split('<br>')[0])

        location_raw = re.sub('<[a-z]{1}>','',str(location_raw).split('\n')[1]).replace('\n','')

        city = re.search('(.*) [A-Z]{2}',location_raw).group(0)[:-3].replace(',','')

        state = re.search('([A-Z]{2})',location_raw).group(0)

        zip = re.search('\d{5,6}',location_raw).group(0)

        # Always comes line after state/zip
        try:
            phone = re.search('\d{3} \d{3} \d{4}',str(href_data.find_all('meta')[5]).replace('(','').replace(')','').replace('-',' ')).group(0)
        except:
            phone = re.search('\d{3} \d{3} \d{4}',str(href_data.find_all('div',{'class':'phone-number'})[0]).replace('(','').replace(')','').replace('-',' ')).group(0)
        phone = ''.join([x for x in phone if x.isnumeric()])

        # hours
        hours_raw = [[[x.text],[y.text.strip() for y in x.find_next_siblings()]] for x in
                     href_data.find_all('td', {'class': 'day'})]
        hours = ' '.join([', '.join(list(itertools.chain(*x))).strip().replace(', ,','').replace('pm,','pm').replace('y,','y:').replace('am,','am') for x in hours_raw])

        # lat long url to parse
        try:
            raw_lat_long = href_data.find_all('div', {'class':'section map'})[0].iframe['src']
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

content = pull_content(location_url)

# Pull all stores and info

final_df = pull_info(content)



# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)