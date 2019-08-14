import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Site URL
site_url = 'http://jinya-ramenbar.com'

# Location URL
location_url = 'https://beachhutdeli.com/locations/'

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

    region_list = soup.find('div',{'id':'content'}).find('div',{'class':'small-12 columns'}).div.find_all('div',{'class':'row'})
    
    for region_item in region_list:
        test_region = region_item.find('div',{'class':'small-12 column'})
        if test_region is not None:
            

            href_datas = region_item.find_all('a')
            for href_datas_list in href_datas:
                href_data = href_datas_list['href']
                city = href_datas_list.text
                
                href_content = pull_content(href_data)
                locator_domain = href_data
                location_name = "<MISSING>"
                street_address = href_content.find('address').text
                state = test_region.text 
               
                zip = str(street_address).split(' ')[len(str(street_address).split(' ')) - 1]
                country_code = "US"
                store_number = "<MISSING>"
                phone = href_content.find('div',{'class','store-contact'}).a.text
             
                store_type = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                ul_for_hours_test = href_content.find('div',{'class':'store-hours'}).find('p')
                if ul_for_hours_test is not None:
                    ul_for_hours = ul_for_hours_test.text
                

        
    
          
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

                ul_for_hours

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