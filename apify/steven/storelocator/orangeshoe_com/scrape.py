import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re
import json


# Location URL
location_url = 'https://www.orangeshoe.com'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content
def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

# Turns java script object into json string
def pull_json(string):
    string = re.sub('(\n|\r)','',string).strip()
    pattern = re.compile(r"(\{.*?\}        \})")
    script = re.findall(pattern,string)[0]
    data = json.loads(script)
    return data

def pull_info(content):

    # list of store hrefs
    store_hrefs = [location_url + x.a['href'] for x in content.find_all('li',{'class':'studioListing'})]

    store_data = []

    for href in store_hrefs:

        href_data = pull_content(href)

        json_string = href_data.find_all('script',{'type':'application/ld+json'})[0]

        store = pull_json(str(json_string))

        store_name = href_data.find_all('span',{'class':'location'})[0].text

        store_type = store['@type']

        street_add = store['address']['streetAddress']

        city = store['address']['addressLocality']

        state = store['address']['addressRegion']

        zip = store['address']['postalCode']

        # Always comes line after state/zip
        phone = ''.join([x for x in store['telephone'] if x.isnumeric()])

        # hours
        hours = '; '.join([x['dayOfWeek'][0] +': ' + x['closes'] for x in store['openingHoursSpecification']])

        lat = store['geo']['latitude']
        long = store['geo']['longitude']



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