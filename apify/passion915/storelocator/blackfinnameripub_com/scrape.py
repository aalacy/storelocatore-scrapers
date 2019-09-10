import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Site URL
site_url = 'http://www.tasteofphilly.biz'
# Location URL
location_url = 'http://blackfinnameripub.com/locations/'

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
    store_list = soup.find('div',{'id':'location_list_wrap'}).find_all('a')

    
    for item in store_list:
        
        city = str(item.text.split(',')[0]).strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        store_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_name = "<MISSING>"


        locator_domain = item['ref']
        ref_id = item['id']
        full_address = soup.find('div',{'id':'location_'+ref_id}).find('div',{'class':'location_address'}).find('input')['value']
        street_address = str(full_address.split(',')[0]).strip().replace('\n',' ')
        zip = str(full_address.split(',')[1]).strip().split(' ')[1]
        state = str(full_address.split(',')[1]).strip().split(' ')[0]
        detail_p = soup.find('div',{'id':'location_'+ref_id}).find('div',{'class':'location_address'}).find_all('p')
        for detail_item in detail_p:
           
            if detail_p.index(detail_item) == 1:
                phone = str(detail_item.text.replace('.','').strip())
        hours_of_operation = soup.find('div',{'id':'location_'+ref_id}).find('div',{'class':'location_hours'}).text.strip()

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