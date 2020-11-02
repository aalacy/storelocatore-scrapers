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
                    locator_domain = store_list_item.a['href'] + '/locations/port-orange/index'
                    location_name = store_list_item.a.text
                    href_data = pull_content(locator_domain)
                    address = href_data.find('div',{'class':'location-address'}).text
                    city = location_name
                    zip = str(address).split(' ')[len(str(address).split(' ')) - 1]
                    state = str(address).split(' ')[len(str(address).split(' ')) - 2]
                    street_address = str(address).replace(state,'').replace(zip,'').replace(',','').strip()
                    country_code = 'US'
                    store_number = '<MISSING>'
                    # phone = str(href_data.find('a',{'class':'zPhoneLink'})['href']).replace('tel:','')
                    phone = href_data.find('a',{'class':'zPhoneLink'}).text
                    store_type = '<MISSING>'
                    
                    data_for_latitude = href_data.find_all('script')
                    for item_latitude in data_for_latitude:
                        if data_for_latitude.index(item_latitude) == 4:
                            longitude = str(str(item_latitude.text.split(':')[1]).split(',')[0]).replace('"','')
                            latitude = str(item_latitude.text.split(':')[4]).replace('"}];','').replace('"','')

                    hours_of_operation = href_data.find('div',{'class':'zEditorHTML'}).text
                else:
                    locator_domain = site_url + store_list_item.a['href']
                   
                    location_name = store_list_item.a.text
                    href_data = pull_content(locator_domain)
                    address = href_data.find('div',{'class':'location-info'}).find('div',{'class':'location-address'}).text.split('\n')[2] + " " + href_data.find('div',{'class':'location-info'}).find('div',{'class':'location-address'}).text.split('\n')[3]
                    city = str(address).split(' ')[len(str(address).split(' ')) - 3].replace(',','')
                    zip = str(address).split(' ')[len(str(address).split(' ')) - 1]
                    state = str(address).split(' ')[len(str(address).split(' ')) - 2]
                    street_address = str(address).replace(state,'').replace(zip,'').replace(',','').strip()
                    country_code = 'US'
                    store_number = '<MISSING>'
                    phone = href_data.find('div',{'class':'location-info'}).find('a',{'class':'zPhoneLink'}).text
                    store_type = '<MISSING>'
                    data_for_latitude = href_data.find_all('script')
                    for item_latitude in data_for_latitude:
                        if data_for_latitude.index(item_latitude) == 7:
                            index_of_store = store_list_li.index(store_list_item)
                            if index_of_store > 6:
                                longitude = str(str(str(item_latitude.text.split('},{')[index_of_store - 1]).split(',')[0]).split(':')[1]).replace('"','')
                                latitude = str(str(item_latitude.text.split('},{')[index_of_store - 1]).split(',')[3]).split(':')[1].replace('"','').replace('}];','')
                            else:
                                longitude = str(str(str(item_latitude.text.split('},{')[index_of_store]).split(',')[0]).split(':')[1]).replace('"','')
                                latitude = str(str(item_latitude.text.split('},{')[index_of_store]).split(',')[3]).split(':')[1].replace('"','')
                           
                        
                    
                    
                    hours_of_operation = href_data.find('div',{'class':'z-2of5 z-m-0 location-info'}).find('div',{'class':'zEditorHTML'}).text
            
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