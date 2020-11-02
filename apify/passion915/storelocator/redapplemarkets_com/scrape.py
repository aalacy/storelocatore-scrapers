import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re
import urllib.request
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('redapplemarkets_com')



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
        logger.info("nth cell is working^^^^^^^^^^^^^^^^^^^^^" + str(store_list.index(item)) )
        cells = item.find_all('td')
        for cell in cells:
            
            if cells.index(cell) == 0:
                city = cell.strong.text.strip()
                location_name = str(cell.text.strip().split('\n')[1]).strip()
               
            elif cells.index(cell) == 1:
                street_address = cell.text
           
            elif cells.index(cell) == 2:
                phone = cell.text
            elif cells.index(cell) == 3:
                logger.info(cell.a['href'])
                if cell.a['href'] == '':
                    logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@link is none____' + location_name)
                    locator_domain = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    state = "<MISSING>"
                    store_type = "<MISSING>"
                    country_code = "US"
                    store_number = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    zip = "<MISSING>"
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
                else:
                    
                    country_code = "US"
                    store_type = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    store_number = "<MISSING>"
                    locator_domain_first = cell.a['href'].replace('//','//www.')
                    
                    
                    logger.info("@@@@@@@@@@@@@@@@@@@@@@at first page there is link+++++++")
                    logger.info('@@@@@@' + location_name)
                    try:
                        test_network = urllib.request.urlopen(locator_domain_first).getcode()
                        if test_network == 200:
                            locator_data = pull_content(locator_domain_first)
                            logger.info("&&&&&&&this link works well")
                            logger.info(test_network)
                            
                            store_infos = locator_data.find_all('li',{'class':'hidden-xs'})
                            for item_store_info_url in store_infos:
                                if item_store_info_url.a.text.strip() == 'Store Info':
                                    
                                    locator_domain_second = item_store_info_url.a['href']
                            logger.info('link is__________' + locator_domain_second)
                            data_of_store = pull_content(locator_domain_second)

                            test_multi = data_of_store.find('div',{'id':'StoreLocator'})

                            if test_multi is not None:
                                logger.info('$$$$$$$$$$$$$$$$$$$this link has more than one stores-----')
                                tr_stores = test_multi.find('table').find_all('tr')
                                for item_tr_stores in tr_stores:
                                    
                                    if tr_stores.index(item_tr_stores) != 0:
                                        
                                        tds = item_tr_stores.find_all('td')
                                        for item_td in tds:
                                            
                                            if tds.index(item_td) == 0:
                                                city = item_td.strong.text
                                                location_name = item_td.em.text
                                                
                                            elif tds.index(item_td) == 1:
                                                street_address = item_td.text
                                                
                                            elif tds.index(item_td) == 2:
                                                phone = str(item_td.a['href']).replace('tel:','').strip()
                                            elif tds.index(item_td) == 3:
                                                locator_domain = item_td.a['href']
                                        
                                        logger.info('url is______' + locator_domain)       
                                        data_of_store_second = pull_content(locator_domain)
                                        if data_of_store_second is not None:
                                            
                                            full_street_address = data_of_store_second.find('p',{'class':'Address'}).text
                                            state = str(full_street_address.split(',')[1]).strip().split(' ')[0]
                                            zip = str(full_street_address.split(',')[1]).strip().split(' ')[1]
                                            table_for_hours = data_of_store_second.find('table',{'id':'hours_info-BS'}).find_all('tr')
                                            for item_of_table in table_for_hours:
                                                if table_for_hours.index(item_of_table) == 0:
                                                    hours_of_operation = item_of_table.td.text    
                                            
                                        else:
                                            state = "MISSING"
                                            zip = "MISSING"
                                            hours_of_operation = "MISSING"
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
                            else:
                                locator_domain = locator_domain_second
                                logger.info('$$$$$$$$$$$$$This link has only one store******************')
                                logger.info('url is_________' + locator_domain)
                                data_of_store_second = pull_content(locator_domain)
                                if data_of_store_second is not None:
                                    full_street_address = data_of_store_second.find('p',{'class':'Address'}).text
                                    state = str(full_street_address.split(',')[1]).strip().split(' ')[0]
                                    zip = str(full_street_address.split(',')[1]).strip().split(' ')[1]
                                    table_for_hours = data_of_store_second.find('table',{'id':'hours_info-BS'}).find_all('tr')
                                    # street_address = full_street_address.replace('Store Address:','').strip().replace('\n',' ').strip()
                                    # city = 
                                    for item_of_table in table_for_hours:
                                        if table_for_hours.index(item_of_table) == 0:
                                            hours_of_operation = item_of_table.td.text
                                


                                else:
                                    state = "MISSING"
                                    zip = "MISSING"
                                    hours_of_operation = "MISSING"
                               
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
                        
                    except:
                        logger.info("&&&&&&&this link does not work well")
                        logger.info(test_network)
                        locator_domain = locator_domain_first
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        state = "<MISSING>"
                        store_type = "<MISSING>"
                        country_code = "US"
                        store_number = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        zip = "<MISSING>"
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