import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://dickshomecare.com/contact/'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'



# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_info(content):

    # list of stores
    location_data = [x for x in content.find_all('section') if 'www.google.com' in str(x)]

    store_data = []

    for store in location_data:

        def clean_up_store(word):
            word = word.replace('</span ','').replace('</span><br/>',' ').replace('</span>','').replace('<br/>','')
            return word
        store_name = "Dickshomecare " + re.search('[A-Za-z]{1,30} Location',clean_up_store(str(store))).group(0).replace('>','')

        store_type = '<MISSING>'

        # Split up address tag to parse
        address_split = re.search('>Address:(.*)</p></div>',str(store)).group(0).replace('>Address:</div><p>','').replace('</br></p></div>','').replace('/>','>').replace('</p></div>','').replace('\xa0',' ').replace('>Address:</div><div><p>','').split('<br>')

        try:
            # determine which piece of list state and city listed. Always one before phone number
            state_city_line = [(id, x) for id, x in enumerate(address_split,0) if re.search('[A-Z]{2} \d{4,6}',x)][0][0]
        except:
            pass

        try:
            city = address_split[state_city_line].split(', ')[0]
        except:
            city = '<INACCESSIBLE>'

        try:
            state = re.findall(' ([A-Za-z]{2}) \d{4,6}', address_split[state_city_line])[0].upper()
        except:
            state = re.findall('>([A-Z]{2})<', str(address_split))[0].upper()

        try:
            zip = re.search('\d{4,6}', address_split[state_city_line]).group(0)
        except:
            try:
                zip = re.search(r'>(\d{4,6})<', str(address_split)).group(0).replace('>','').replace('<','')
            except:
                zip = '<INACCESSIBLE>'

        # No consistency to locate besides format of phone
        phone = re.search('\d{3}-\d{3}-\d{4}', str(store)).group(0)
        phone = ''.join([x for x in phone if x.isnumeric()])

        # Concatenate all parts of list prior to city state for street address
        street_add = ' '.join([x for x in address_split[0:state_city_line] if x != ''])
        street_add = '<INACCESSIBLE>' if '<' in street_add else street_add

        # hours
        hours = re.search('<p>Hours:(.*)</p></div>',str(store)).group(0).replace('<p>Hours: ','').replace('</p></div>','').replace('<br/>',',')

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

            hours,

            address_split

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

        'hours_of_operation',

        'raw_address']



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df



# Pull URL Content

soup = pull_content(location_url)



# Pull all stores and info

final_df = pull_info(soup)



# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)