import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Site URL


# Location URL
location_url = 'https://www.letsyoyogurt.com/find-a-location'

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

    tr_region_list = soup.find('table').tbody.find_all('tr')
    
    for tr_region_item in tr_region_list:
        td_dec_store = tr_region_item.find_all('td')
        for td_dec_item in td_dec_store:
            if td_dec_store.index(td_dec_item) == 0:
                locator_domain = "<MISSING>"
                location_name = "Let's Yo"
                street_address = td_dec_item.find('div',{'class':'street-address'}).text.replace('\n','')
                store_number = "<MISSING>"
                city = td_dec_item.find('span',{'class':'locality'}).text
                state = td_dec_item.find('span',{'class':'region'}).text
                zip = td_dec_item.find('span',{'class':'postal-code'}).text
                latitude = td_dec_item.find('div',{'class':'hidden'})['data-lat']
                longitude = td_dec_item.find('div',{'class':'hidden'})['data-long']
                country_code = td_dec_item.find('div',{'class':'location-hidden'}).text.replace('\n','').replace(state,'')
                
                
            elif td_dec_store.index(td_dec_item) == 1:
                phone = td_dec_item.a.text
            store_type = "<MISSING>"
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