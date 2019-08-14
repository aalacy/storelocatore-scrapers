import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Site URL
site_url = 'http://www.tasteofphilly.biz'
# Location URL
location_url = 'https://www.freshtoorder.com/locate/'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_info(content):
 

    store_data = []
    store_list = soup.find('div',{'class':'mpfy-mll-list'}).find_all('div',{'class':'mpfy-mll-location'})

    
    for item in store_list:
        locator_domain = "<MISSING>"
        location_name = str(item.find('div',{'class':'mpfy-mll-l-title'}).text).split('\n')[1]
        
        street_address = item.find('div',{'class':'mpfy-mll-l-content'}).find('div',{'class':'location-address'}).text
        phone = item.find('div',{'class':'mpfy-mll-l-content'}).find('div',{'class':'contact-details'}).text
        city = str(street_address).split(',')[len(str(street_address).split(',')) - 3]
        zip = str(street_address).split(',')[len(str(street_address).split(',')) - 1]
        state = str(street_address).split(',')[len(str(street_address).split(',')) - 2]
        latitude = item['data-lat']
        longitude = item['data-lng']
        country_code = "US"
        store_number = "<MISSING>"
        store_type = "<MISSING>"
        hours_of_operation = item.find('div',{'class':'mpfy-mll-l-content'}).find('div',{'class':'location-hours'}).text

        temp_data = [

            locator_domain,

            location_name,

            street_address,

            city,

            state,

            zip,

            country_code,

            store_number,

            phone,

            store_type,

            latitude,

            longitude,

            hours_of_operation

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
       
        

       


                         



# # Pull URL Content

soup = pull_content(location_url)

# # Pull all stores and info

final_df = pull_info(soup)



# # write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)