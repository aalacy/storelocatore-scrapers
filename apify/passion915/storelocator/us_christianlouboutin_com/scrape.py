import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Site URL
site_url = 'https://www.wyndhamhotels.com'
# Location URL
location_url = 'https://us.christianlouboutin.com/ot_en/storelocator/all-stores'

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
    list_continent = soup.find_all('li',{'class':'continent'})

    
    for item_continent in list_continent:
        continent_name = item_continent.span['data-label']
        contient_countries = item_continent.ul.find_all('li')
        
        for country_item in contient_countries:
            country_code = country_item.a['data-label']
            country_href = country_item.a['href']

            content_country = pull_content(country_href)
            
            test_state = content_country.find('div',{'class':'store'})
            
            if test_state is not None:

                list_stores = content_country.find('div',{'class':'store'}).find_all('a',{'class':'item'})
                
                for item_store in list_stores:
                    
                    store_href = item_store['href']
                    
                    locator_domain = store_href
                    
                    content_store = pull_content(locator_domain)
                    test_ok = content_store.find('div',{'id':'store-information'})
                    if test_ok is not None:
                        # location_name = content_store.find('div',{'id':'store-information'}).find('hgroup').find('htag1').text
                        
                        location_name = content_store.find('hgroup').div.find('htag1').text
                        street_address = content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'address1'}).text + " " + content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'address2'}).text
                        city = content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'city'}).text
                        state = "<MISSING>"
                        zip = content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'address2'}).text
                        
                        store_number = "<MISSING>"
                        phone = content_store.find('span',{'itemprop':'telephone'}).text
                        store_type = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        hours_of_operation = content_store.find('div',{'class':'hours'}).ul.text

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