import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rmcf_com')



# Location URL
location_url = 'https://www.rmcf.com/locations'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_info(content):

    # list of store hrefs
    store_hrefs = [x.a['href'] for x in content.find_all('tr') if x.a]

    store_data = []

    for href in store_hrefs:

        # Some HREFs are broken
        try:
            # Pull store page
            store = pull_content('https://www.rmcf.com' + href).find_all('div', {'class': 'store-locations-detail'})[0]

            # Only include US pages
            country_cd = store.find('dd',{'id':'cityStateZipInfo'}).find_next_sibling().find_next_sibling().text
            if country_cd == 'US':

                store_name = store.h1.text

                # Number is stripped out of href
                store_num = ''.join([x for x in href if x.isnumeric()])

                # Unknown
                store_type = '<MISSING>'

                # location info
                street_add = store.find('dd',{'id':'addyInfo'}).text
                city = store.find('dd',{'id':'cityStateZipInfo'}).text.split(',')[0]
                state = store.find('dd',{'id':'cityStateZipInfo'}).text.split(',')[1].strip().split(' ')[0]
                zip = store.find('dd',{'id':'cityStateZipInfo'}).text.split(',')[1].strip().split(' ')[1]

                # Pull only numeric characters from phone listing
                phone = [x.find_next_sibling().text for x in store.find_all('dt') if re.search('\d{3}-\d{3}-\d{4}',x.find_next_sibling().text)][0]
                phone = ''.join([x for x in phone if x.isnumeric()])

                # hours aren't listed
                hours = ''
                hours = hours if 'PM' in hours else '<MISSING>'

                # lat long url to parse (isn't available in the google.com/maps SDC
                lat = '<MISSING>'
                long = '<MISSING>'

                #co-brand
                try:
                    co_brand = store.find_all('div',{'id':'ctl00_ctl00_NestedMaster_PageContent_coBrandPanel'})[0].text
                    co_brand = co_brand.replace('\nCo-Brand:\n','').replace('\n','')
                    co_brand = 'N/A' if co_brand=='' else co_brand
                except:
                    co_brand = 'N/A'

                temp_data = [

                    'https://www.rmcf.com' + href,

                    store_name,

                    street_add,

                    city,

                    state,

                    zip,

                    country_cd,

                    store_num,

                    phone,

                    store_type,

                    lat,

                    long,

                    hours,

                    co_brand

                ]



                store_data = store_data + [temp_data]

        except:
            logger.info('Bad HREF: %s' % href)

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

        'hours_of_operation',

        'co_brand']



    final_df = pd.DataFrame(store_data,columns=final_columns)


    return final_df



# Pull URL Content

content = pull_content(location_url)

# Pull all stores and info

final_df = pull_info(content)


# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)