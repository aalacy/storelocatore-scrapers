import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import re
import os

# Location URL
location_url = 'https://bigskyfitness.com/'
# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))
# file name of CSV output
file_name = 'data.csv'

# Function pull webpage content
def pull_content(url):
    soup = bs(r.get(url).content,'html.parser')
    return soup

def pull_info(content):

    # pull out list of locations hrefs
    location_urls = [x.a['href'] for x in content.find_all('ul', {'class':'sub-menu'})[0] if x!='\n']
    # Some are missing url prefix
    location_urls = ['https://bigskyfitness.com' + x if 'com' not in x else x for x in location_urls]

    store_data = []
    # loop through each href
    for href in location_urls:

        content = pull_content(href)

        street_add = re.findall('<h5>(.*)<br/>',str(content.h5))[0].title()
        city = re.findall('<br/>\n(.*), ',str(content.h5))[0].title()
        store_name = 'Big Sky Fitness - ' + city
        state = re.findall(', ([A-Za-z]{2}) ',str(content.h5))[0].upper()
        zip = re.findall(', [A-Za-z]{2} (\d{4,5})',str(content.h5))[0]
        phone = ''.join([x for x in content.h3.text if x.isnumeric()])
        try:
            hours_raw = str(content.find_all('div', {'class':'mk-text-block'})).replace('\n','').replace('mon-thurs','mon-thu').replace('- ','-').replace(' &amp; ','&')
            hours = re.findall('<p>club hours<br/>(mon-thu \d:\d\d[a-z]{1}-\d{1,2}[a-z]{1}<br/>friday \d:\d\d[a-z]{1}-\d{1,2}[a-z]{1}<br/>saturday \d:\d\d[a-z]{1}-\d{1,2}[a-z]{1}<br/>sunday \d:\d\d[a-z]{1}-\d{1,2}[a-z]{1})',hours_raw)[0].replace('<br/>','; ')
        except:
            try:
                hours = re.findall(
                    '<p>club hours<br/>(mon-thu \d{1,2}[a-z]{1}-\d{1,2}[a-z]{1}<br/>fri \d{1,2}[a-z]{1}-\d{1,2}[a-z]{1}<br/>sat&sun \d{1,2}[a-z]{1}-\d{1,2}[a-z]{1})',
                    hours_raw)[0].replace('<br/>', '; ')
            except:
                if '<p>club hours<br/>' in hours_raw:
                    hours = '<INACCESSIBLE>'
                else:
                    hours = '<MISSING>'
        try:
            raw_lat_long = content.find_all('div', {'class':'wpb_map_wraper'})[0].iframe['src']
            long = re.search('!2d(.*)!3d',raw_lat_long).group(0).replace('!2d','').replace('!3d','')
            lat = re.search('!3d(.*)!3m2!',raw_lat_long).group(0).replace('!3d','')[:7]
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
            '<MISSING>',
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
