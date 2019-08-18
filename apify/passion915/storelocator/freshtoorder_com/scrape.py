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
        address = item.find('div',{'class':'location-address'}).strong.text.strip()
        state = address.split(',')[len(address.split(',')) - 2]
        zip = address.split(',')[len(address.split(',')) - 1]
        street_address = str(address.split('|')[0]).strip().replace('.','')
        test_phone = item.find('div',{'class':'mpfy-mll-l-content'}).find('div',{'class':'contact-details'}).p
        if test_phone is None:
            phone = "<MISSING>"
        else:
            phone = test_phone.text.strip()
        city = str(str(address.split('|')[1]).split(',')[0]).strip()

        latitude = item['data-lat']
        longitude = item['data-lng']
        country_code = "US"
        store_number = "<MISSING>"
        store_type = "<MISSING>"
        test_hours = item.find('div',{'class':'mpfy-mll-l-content'}).find('div',{'class':'location-hours'})
        if test_hours.p is None:
            hours_of_operation = "<MISSING>"
        else:
            hours_of_operation = test_hours.text.strip()
   

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