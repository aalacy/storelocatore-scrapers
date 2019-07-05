import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import re

# Location URL
location_url = 'http://www.bkpilates.com/'
# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__)
# file name of CSV output
file_name = 'bkpilates_extract.csv'

# Function pull webpage content
def pull_content(url):
    soup = bs(r.get(url).content,'html.parser')
    return soup

def pull_info(content):

    location_data = content.find_all('div', {'class':'widget widget_text grid3'})

    store_data = []
    for store in location_data:
        store_name = store.h2.text
        split_data = store.p.text.split('\n')
        street_add = re.sub(', $','',split_data[0])
        city = re.findall('(.*), [A-Za-z]{2}',split_data[1])[0]
        state = re.findall(', ([A-Za-z]{2}) ', split_data[1])[0]
        zip = re.findall(', [A-Za-z]{2} (\d{4,5})', split_data[1])[0]
        phone = ''.join([x for x in split_data[2] if x.isnumeric()])
        try:
            hour_lists = [(id) for id,x in enumerate(split_data,1) if '0pm' in x]
            hours = '; '.join([x.replace('           ',' ').
                              replace('         ',' ').replace('  ',' ') for x in split_data[min(hour_lists)-1:max(hour_lists)]])
        except:
            hours = None

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



