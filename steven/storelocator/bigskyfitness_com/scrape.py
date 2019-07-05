import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import re

# Location URL
location_url = 'https://www.blackeyedpeacolorado.com/index.php/locations'
# output path of CSV
output_path = 'C:/Users\spiscatelli\PycharmProjects\Code\Free Lance\SafeWork Scraping'
# file name of CSV output
file_name = 'blackeyepea_extract.csv'

# Function pull webpage content
def pull_content(url):
    soup = bs(r.get(url).content,'html.parser')
    return soup

def pull_info(content):

    location_data = content.find_all('div', {'class': 'el-content uk-margin'})

    store_data = []
    for store in location_data:
        split_data = store.p.text.split('\n')
        street_add = re.findall('<p>(.*)<br/>',str(store))[0]
        city = re.findall('<br/>(.*), ',str(store))[0]
        state = re.findall(', ([A-Za-z]{2}) ',str(store))[0]
        store_name = 'Black-eyed Pea ' + city
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
            '<MISSING>'
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