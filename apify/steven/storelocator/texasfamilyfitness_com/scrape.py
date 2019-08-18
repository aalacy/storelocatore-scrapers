import pandas as pd
import requests as r
import os
from bs4 import BeautifulSoup as bs
import re

#TODO: Update requirements file and all dependency files.
#TODO: Ask how to handle preview vs open facilities

# Location URL
location_url = 'https://www.texasfamilyfitness.com/locations?hsCtaTracking=caf4867a-b816-4709-999d-1eebe027f30f%7Cb5b9f7ad-b642-4020-bc2c-138fe5f58a13'

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
    soup = bs(r.get(url,headers=header).content,'html.parser')

    return soup

def pull_info(content):

    # list of store hrefs
    stores = content.find_all('div',{'class':'location'})

    store_data = []

    for store in stores:

        store_name = store.h2.text

        store_type = '<MISSING>'

        store_number = '<MISSING>'

        try:
            street_add = str(store.p).split('<br/>')[0].replace('<p>','')

            city = str(store.p).split('<br/>')[1].replace('</p>','').split(',')[0]

            state = re.search('[A-Z]{2} ',str(store.p).split('<br/>')[1].replace('</p>','').split(',')[1]).group(0).strip()

            zip = re.search('[A-Z]{2} (\d{4,6})',str(store.p).split('<br/>')[1].replace('</p>','').split(',')[1]).group(0).strip()[3:]
        except:

            street_add = store.find('div', {'class': 'address'}).p.text.replace('\xa0', '')

            city = store.find('div', {'class': 'address'}).p.find_next().text.split(',')[0]

            state = re.search('[A-Z]{2} ', store.find('div', {'class': 'address'}).p.find_next().text).group(0).strip()

            zip = re.search('[A-Z]{2} (\d{4,6})', store.find('div', {'class': 'address'}).p.find_next().text).group(
                0).strip()[3:]

        phone = ''.join([x for x in store.find('div',{'class':'phone'}).text if x.isnumeric()])

        hours = store.find('div',{'class':'club-hours-container'}).text.replace('\n',' ').strip() + \
                '; ' + store.find('div',{'class':'kids-club-hours-container'}).text.replace('\n',' ').strip()

        lat = store['data-location-lat']

        long = store['data-location-lng']



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

        'hours_of_operation'

        ]



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df





# Pull URL Content
content = pull_content(location_url)

# Pull all stores and info
final_df = pull_info(content)

# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)