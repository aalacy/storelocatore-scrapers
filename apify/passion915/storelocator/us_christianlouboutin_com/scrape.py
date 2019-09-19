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
def get_country_code(country_name):
    if country_name == 'Canada':
        return 'CA'
    elif country_name == 'United States':
        return 'US'
    
def pull_info(content):
 

    store_data = []
    list_continent = soup.find_all('li',{'class':'continent'})

    
    for item_continent in list_continent:
        continent_name = item_continent.span['data-label']
        contient_countries = item_continent.ul.find_all('li')
        
        for country_item in contient_countries:
            country_code = get_country_code(str(country_item.a['data-label']).strip())
            if country_code == 'CA' or country_code == 'US':
                country_href = country_item.a['href']
                
                content_country = pull_content(country_href)
                
                test_state = content_country.find('div',{'class':'store'})
                
                if test_state is not None:

                    list_stores = content_country.find('div',{'class':'store'}).find_all('a',{'class':'item'})
                    
                    for item_store in list_stores:
                        
                        store_href = item_store['href']
                        
                        locator_domain = store_href
                        
                        content_store = pull_content(locator_domain)
                        location_name = item_store.find('span',{'class':'name'}).text.strip()
                        full_street_address = item_store.find_all('span',{'class':'address'})
                        for item_address in full_street_address:
                            if full_street_address.index(item_address) == 0:
                                street_address = item_address.text
                            elif full_street_address.index(item_address) == 1:
                                zip = item_address.text
                        state = item_store.find('span',{'itemprop':'addressLocality'}).text.strip()
                        if zip == 'Floor':
                            zip = "<MISSING>"
                        test_ok = content_store.find('htag1',{'itemprop':'name'})
                        if test_ok is not None:

                            
                            # street_address = content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'address1'}).text + " " + content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'address2'}).text
                            city = content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'city'}).text
                            # state = "<MISSING>"
                            # print(locator_domain)
                            # if content_store.find('span',{'class':'address2'}).text == '':
                                # zip = "<MISSING>"
                            # else:
                            #     string_for_zip = content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'address2'}).text.strip()
                            #     # print(string_for_zip)
                            #     if country_code == "CA":
                            #         zip = string_for_zip.replace('CA','').strip().split(' ')[len(string_for_zip.replace('CA','').strip().split(' ')) -2] + " " + string_for_zip.strip().replace('CA','').split(' ')[len(string_for_zip.replace('CA','').strip().split(' ')) -1]
                            #     else:
                            #         if len(string_for_zip.split(' ')) > 1:
                            #             zip = str(string_for_zip.replace('US','').strip().split(' ')[len(string_for_zip.replace('US','').strip().split(' ')) - 1]).strip()
                            #         else:
                                    
                            #             zip = string_for_zip
                            
                        
                            store_number = "<MISSING>"
                            phone_test = content_store.find('div',{'class':'cols clearfix'}).find('a',{'class':'tel btn'})
                            if phone_test is None:
                                phone = "<MISSING>"
                            else:
                                phone = phone_test['href'].replace('tel:','').replace('Option 1','').replace('- OPTION 1','').replace('- OPTION 2','').replace('- Option 1','').strip()
                
                            store_type = "<MISSING>"
                            latitude = "<MISSING>"
                            longitude = "<MISSING>"
                            hours_of_operation = content_store.find('div',{'class':'hours'}).ul.text.strip()
                        else:
                            
                            street_address = "<MISSING>"
                            city = "<MISSING>"
                            state = "<MISSING>"
                            zip = "<MISSING>"
                            store_number = "<MISSING>"
                            phone = "<MISSING>"
                            store_type = "<MISSING>"
                            latitude = "<MISSING>"
                            longitude = "<MISSING>"
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
                # else:
                
                #     store_href = country_href
                        
                #     locator_domain = store_href
                    
                #     content_store = pull_content(locator_domain)
                #     test_ok = content_store.find('div',{'id':'store-information'})
                #     if test_ok is not None:
            
                #         location_name = content_store.find('hgroup').div.find('htag1').text.strip()
                #         street_address = content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'address1'}).text + " " + content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'address2'}).text
                #         city = content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'city'}).text
                #         state = "<MISSING>"
                #         if content_store.find('span',{'class':'address2'}).text == '':
                #             zip = "<MISSING>"
                #         else:
                #             string_for_zip = content_store.find('hgroup').find('div',{'class':'text'}).find('htag4').find('span',{'class':'address2'}).text
                #             zip = string_for_zip
                        
                #         store_number = "<MISSING>"
                #         phone_test = content_store.find('div',{'class':'cols clearfix'}).find('a',{'class':'tel btn'})
                #         if phone_test is None:
                #             phone = "<MISSING>"
                #         else:
                #             phone = str(phone_test['href']).replace('tel:','').replace('Option 1','').replace('- OPTION 1','').replace('- Option 1','').replace('- OPTION 2','').strip()
                #         store_type = "<MISSING>"
                #         latitude = "<MISSING>"
                #         longitude = "<MISSING>"
                #         hours_of_operation = content_store.find('div',{'class':'hours'}).ul.text.strip()

                #     temp_data = [

                #         locator_domain,

                #         location_name,

                #         street_address,

                #         city,

                #         state,

                #         zip,

                #         country_code,

                #         store_number,

                #         phone,

                #         store_type,

                #         latitude,

                #         longitude,

                #         hours_of_operation

                #     ]
                #     store_data = store_data + [temp_data]
 
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