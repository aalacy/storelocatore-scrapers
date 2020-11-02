import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Site URL
site_url = 'http://jinya-ramenbar.com'

# Location URL
location_url = 'http://jinya-ramenbar.com/locations/'

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

    region_list = soup.find_all('dl')
    for region_item in region_list:
        
        region_store_list = region_item.find_all('dd')
        for store in region_store_list:

            locator_domain = site_url + store.find('a')['href']
            location_name = store.find('div',{'class':'shop-name'}).text
            address = store.find('div').find('div',{'class':'shop-address'}).text
            city = store.find('div',{'class':'shop-name'}).text.replace('(Coming Soon)','').split('|')[0]

            # test = str(str(address).split(' ')[len(str(address).split(' ')) - 1]).strip()
            test = 'Canada' in address
            if test:
                country_code = "CA"
                state_zip = address.split(',')[len(str(address).split(',')) - 1]
                if len(str(address.replace(',','')).split(' ')[len(str(address).split(' ')) - 2]) == 3:
                    zip = str(address.replace(',','')).split(' ')[len(str(address).split(' ')) - 3] + " " + str(address.replace(',','')).split(' ')[len(str(address).split(' ')) - 2]
                    
                else:
                    zip =  str(address.replace(',','')).split(' ')[len(str(address).split(' ')) - 2]
                test_for_state = str(str(address).split(',')[len(str(address).split(',')) - 1]).strip()
                if test_for_state == 'Canada':
                    state = str(str(address).split(',')[len(str(address).split(',')) - 2]).replace(zip, '').replace(',','') 
                else:
                    state = str(str(address).split(',')[len(str(address).split(',')) - 1]).replace(zip, '').replace('Canada','').replace(',','') 
                
                
             
            else:
                state = str(address).split(' ')[len(str(address).split(' ')) - 2]

                zip = str(address).split(' ')[len(str(address).split(' ')) - 1]
                country_code = "US"

            
            street_address = address.replace(zip, '').replace(state, '').replace('Canada','').replace(',','')
           

            
            
            
            country_code = "US"
            store_number = "<MISSING>"
            
            href_data = pull_content(locator_domain)
            
            phone_test = len(str(href_data.find('div',{'class':'shop-text'}).find('h3').text.strip().split('\n')[0]))
            if phone_test < 5:
                phone = "<MISSING>"
            else:
                phone = str(str(href_data.find('div',{'class':'shop-text'}).find('h3').text.strip().split('\n')[0]).encode("utf-8")).replace('b','').replace("'","")
     
            store_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            
            ul_for_hours = href_data.find('div',{'class':'shop-text'}).find('ul').find('li').text
            if ul_for_hours == '':
                hours_of_operation = "<MISSING>"
            else:
                hours_of_operation = ul_for_hours


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