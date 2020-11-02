import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('doctorsonduty_com')




# Location URL
location_url = 'http://doctorsonduty.com/locations/'

# output path of CSV
#output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_info(content):

    # list of stores
    stores = [x for x in content.find_all('div',{'class':'elementor-column-wrap elementor-element-populated'}) if 'Clinic Manager' in str(x)]

    store_data = []

    for store in stores:

        store_name = store.h2.text

        store_type = '<MISSING>'
        logger.info(store_name)
        add_phone_hour_split = [x for x in store.find_all('div',{'class':'elementor-text-editor elementor-clearfix'})[0].text.replace('<br>','\n').replace('Blvd','Blvd\n').replace('Ave','Ave\n').replace(' St',' St\n').split('\n')
                                if (x != '')&(x!=', St')&(x!='e A')]

        #store.find_all('div',{'class':'elementor-text-editor elementor-clearfix'})[0].br.text
        # This works for the ones that failed.  'Marina, CA 93933(831) 883-3330 (ph)(831) 883-3335 (f)'
        # have to split the .p with the city from the above string
        street_add = add_phone_hour_split[0]

        city = add_phone_hour_split[1].split(',')[0]

        state = re.search('[A-Z]{2}',add_phone_hour_split[1]).group(0)

        zip = re.search('\d{5}',add_phone_hour_split[1]).group(0)

        # Always comes line after state/zip
        try:
            phone = ''.join([x for x in add_phone_hour_split[2] if x.isnumeric()])
        except:
            phone = re.search('\d{3} \d{3}-\d{4}', add_phone_hour_split[1].replace('(', ' ').replace(')', '')).group(0)
            phone = ''.join([x for x in phone if x.isnumeric()])

        # hours
        try:
            hours = add_phone_hour_split[4].replace('Days/Hours: ','').strip()
        except:
            hours = re.search('Days/Hours:(.*).Clinic', add_phone_hour_split[1]).group(0).replace('\xa0', '').replace(
                'Days/Hours:', '').replace('.Clinic', '').strip()

        # lat long url to parse
        lat = '<MISSING>'
        long = '<MISSING>'



        temp_data = [

            location_url,

            store_name,

            street_add,

            city,

            state,

            zip,

            'US',

            '<MISSING>',

            phone,

            store_type,

            lat,

            long,

            hours.replace('Days/Hours: ','')

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



# Pull URL Content

content = pull_content(location_url)

# Pull all stores and info

final_df = pull_info(content).drop_duplicates()



# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)