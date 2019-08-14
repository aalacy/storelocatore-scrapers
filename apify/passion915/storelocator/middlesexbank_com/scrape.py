import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Site URL
site_url = 'https://www.middlesexbank.com'
# Location URL
location_url = 'https://www.middlesexbank.com/locations'

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
    store_list = soup.find_all('li',{'class':'branch'})
    
    for store_item in store_list:

        street_address = store_item['data-address']
        latitude = store_item['data-lat']
        longitude = store_item['data-lng']

        test = store_item.find('a',{'class':'ext'})
        location_name = "<MISSING>"
        state = str(street_address).split(' ')[len(str(street_address).split(' ')) - 2]
        zip = str(street_address).split(' ')[len(str(street_address).split(' ')) - 1]
        store_type = "<MISSING>"
        country_code = "UK"
        if test is None:
            city = store_item.find('a',{'class':'location-title'}).text
            locator_domain = site_url + store_item.find('a',{'class':'visit-page'})['href']
            href_data = pull_content(locator_domain)
            phone = href_data.find('span',{'property':'telephone'}).a.text
            store_number = "<MISSING>"
            hours_of_operation = href_data.find('div',{'property':'openingHours'}).text
            

        else:
            city = "<MISSING>"  
            locator_domain = "<MISSING>" 
            href_data = "<MISSING>"
            phone = "<MISSING>"
            store_number = "<MISSING>"
            hours_of_operation = "<MISSING>"

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