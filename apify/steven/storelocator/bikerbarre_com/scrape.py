import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import re
import os

# Location URL
location_url = 'https://bikerbarre.com/'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'

# Function pull webpage content
def pull_content(url):
    soup = bs(r.get(url).content,'html.parser')
    return soup

def pull_info(content):

    location_data = content.find_all('div',{'class':'col-md-3 locations'})[0].find_all('div')

    store_data = []
    for store in location_data:
        store_name = store.p.text.split('\n')[0]
        street_add = re.findall('\t\t\t\t\t\t\t\t(.*)<br/>\n\t',str(store))[0]
        city = re.findall('<br/>\n\t\t\t\t\t\t\t\t(.*), ',str(store))[0]
        state = re.findall(', ([A-Za-z]{2}) ',str(store))[0]
        zip = re.findall(', [A-Za-z]{2} (\d{4,5})',str(store))[0]
        phone = ''.join([x for x in store.a['href'] if x.isnumeric()])

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
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<INACCESSIBLE>'
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
