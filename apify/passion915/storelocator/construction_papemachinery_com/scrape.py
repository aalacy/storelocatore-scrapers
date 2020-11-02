import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re

# Site URL
site_url = 'https://construction.papemachinery.com'

# Location URL
location_url = 'https://construction.papemachinery.com/locations'

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

    location_list = soup.find('ul',{'id':'location-list'}).find_all('li')

    for location_item in location_list:
        

        
        locator_domain = location_item.find('div',{'class','details-left'}).find('a',{'class':'location-name'})['href']
        
        location_name = location_item.find('div',{'class','details-left'}).find('a',{'class':'location-name'}).text
        
        href_data = pull_content(locator_domain)
        address = href_data.find('address').text
        city = location_name.split(',')[0]
        street_address = str(str(href_data.find('address').text).replace('E.','').split(',')[0]).strip().replace('\n','').split('\t')[0] + " " + city
   

        
    
        state = str(str(str(href_data.find('address')).split('<br/>')[1]).split(',')[1]).replace('</address>','').strip().split(' ')[0]
   
        # zip = str(str(href_data.find('address').text).split(',')[1]).strip().split(" ")[1]
        zip = str(str(str(href_data.find('address')).split('<br/>')[1]).split(',')[1]).replace('</address>','').strip().split(' ')[1]
        
        country_code = "US"
        store_number = "<MISSING>"
        
        phone = str(href_data.find('span',{'class':'fe-phone-swap'}).find('a')['href']).replace('tel:','')
        index_of_store = location_list.index(location_item)
 
        data_for_latitude = soup.find_all('script')
        for item_for_latitude in data_for_latitude:
            if data_for_latitude.index(item_for_latitude) == 11:
                
                s = str(item_for_latitude.text.split('},{')[index_of_store])
                result_lat = re.search("latitude':(.*)'longitude", s)
                latitude = str(result_lat.group(1)).replace(',','')
                result_lng = re.search("longitude':(.*),'makeTitles", s)
                longitude = result_lng.group(1).replace(',','')
                

        store_type = "<MISSING>"
        
        
        test_hours = href_data.find('aside').table

        
        if test_hours is not None:
            list_hours = href_data.find('aside').find('table',{'class':'simple'}).find('tbody').find_all('tr')
            ul_for_hours = ""
            for item_hours in list_hours:
                ul_for_hours = ul_for_hours + item_hours.text + "\n"
       
        else:
            ul_for_hours = "No hours"
        

        
        
        hours_of_operation = ul_for_hours.strip()
          
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