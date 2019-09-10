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

        test = store_item.find('a',{'class':'ext'})
        if test is None:
            address = store_item['data-address']
            latitude = store_item['data-lat']
            longitude = store_item['data-lng']

            
            location_name = store_item.find('a',{'class':'location-title'}).text
            # if str(str(address).split(' ')[len(str(address).split(' ')) - 2]).strip() == 'MA':
            state = str(str(address).split(' ')[len(str(address).split(' ')) - 2]).strip()
            
            
            zip = str(str(address).split(' ')[len(str(address).split(' ')) - 1]).strip()
            street_address = str(address).replace(state,'').replace(zip,'').replace(',','')
            store_type = "<MISSING>"
            country_code = "US"
            city = str(address.split(',')[1]).replace(zip,'').replace(state,'').strip()
            locator_domain = site_url + store_item.find('a',{'class':'visit-page'})['href']
            href_data = pull_content(locator_domain)
            phone = href_data.find('span',{'property':'telephone'}).a.text
            store_number = "<MISSING>"
            hours_of_operation = href_data.find('div',{'property':'openingHours'}).text.strip()
        else:
            break
     

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