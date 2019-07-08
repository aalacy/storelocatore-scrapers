import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os


# Location URL
location_url = 'https://www.thebeneficial.com/locations'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'



# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup



def pull_info(content):

    location_data = content.find_all('tr',{'class':'individualLocation'})


    store_data = []

    for store in location_data:

        store_name = store.find_all('td')[1].text

        store_type = store.find_all('td')[2].text

        street_add = store.find_all('td')[3].text

        city = store.find_all('td')[5].text

        state = store.find_all('td')[6].text.strip()

        zip = store.find_all('td')[7].text

        phone = ''.join([x for x in store.find_all('td')[8].text if x.isnumeric()])

        hours = store.find_all('td')[13].text

        lat = store.find_all('td')[15].text

        long = store.find_all('td')[16].text



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