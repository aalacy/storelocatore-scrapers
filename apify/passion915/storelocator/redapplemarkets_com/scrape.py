import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://www.redapplemarkets.com/locations'

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
    store_list = soup.find('table').tbody.find_all('tr')

    for item in store_list:
        cells = item.find_all('td')
        for cell in cells:
            if cells.index(cell) == 0:
                city = cell.strong.text
                location_name = cell.text.replace(city, '').replace('\n','')
            elif cells.index(cell) == 1:
                street_address = cell.text
           
            elif cells.index(cell) == 2:
                phone = cell.text
            else:
                if cell.a['href'] == '':
                    locator_domain = 'no data'
                else:
                    locator_domain = cell.a['href']
                
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                state = "<MISSING>"
                zip = "<MISSING>"
                store_type = "<MISSING>"
                country_code = "UK"
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