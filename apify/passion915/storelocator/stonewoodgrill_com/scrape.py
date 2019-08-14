import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Site URL
site_url = 'https://www.stonewoodgrill.com'
# Location URL
location_url = 'https://www.stonewoodgrill.com/locations/index'

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
    footer_menu_content = soup.find_all('ul',{'class':'footer-menu'})

    
    for footer_menu_list in footer_menu_content:
        if footer_menu_content.index(footer_menu_list) == 2:
            store_list_li = footer_menu_list.li.ul.find_all('li')
            for store_list_item in store_list_li:
                
                if store_list_li.index(store_list_item) == 6:
                    locator_domain = store_list_item.a['href']
                    location_name = '<MISSING>'
                    href_data = '<MISSING>'
                    street_address = '<MISSING>'
                    city = '<MISSING>'
                    zip = '<MISSING>'
                    state = '<MISSING>'
                    country_code = 'US'
                    store_number = '<MISSING>'
                    phone = '<MISSING>'
                    store_type = '<MISSING>'
                    latitude = '<MISSING>'
                    longitude = '<MISSING>'
                    hours_of_operation = '<MISSING>'
                else:
                    locator_domain = site_url + store_list_item.a['href']
                   
                    location_name = store_list_item.a.text
                    href_data = pull_content(locator_domain)
                    street_address = href_data.find('div',{'class':'location-info'}).find('div',{'class':'location-address'}).text.split('\n')[2] + " " + href_data.find('div',{'class':'location-info'}).find('div',{'class':'location-address'}).text.split('\n')[3]
                    city = str(street_address).split(' ')[len(str(street_address).split(' ')) - 3].replace(',','')
                    zip = str(street_address).split(' ')[len(str(street_address).split(' ')) - 1]
                    state = str(street_address).split(' ')[len(str(street_address).split(' ')) - 2]
                    country_code = 'US'
                    store_number = '<MISSING>'
                    phone = href_data.find('div',{'class':'location-info'}).find('a',{'class':'zPhoneLink'}).text
                    store_type = '<MISSING>'
                    latitude = '<MISSING>'
                    longitude = '<MISSING>'
                    hours_of_operation = href_data.find('div',{'class':'location-hours'}).find('div',{'class':'zEditorHTML'}).text.replace('pmMon','pm Mon').replace('pmFri','pm Fri')
                   
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