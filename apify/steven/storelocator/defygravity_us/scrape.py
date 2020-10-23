import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('defygravity_us')



# Location URL
location_url = 'http://www.defygravity.us/'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content

def pull_content(url):

    soup = bs(r.get(url).content,'html.parser')

    return soup

def pull_info(content):
    """
    Awful website. Every store has a different webpage format (including xpaths)
    - 4 different try statements below for each of the stores.
        - Hopefully in the future (if stores added), the format will mimic one of them
    """


    # list of store hrefs
    store_hrefs = [x['href'] for x in content.ul.find_all('a')]

    store_data = []

    for href in store_hrefs:

        logger.info(href)

        store = pull_content(href)

        store_name = re.sub('(\r|\n|\t)','',str(store.title.text)).split(',')[0].split('|')[0].split(':')[0].strip()

        store_type = '<MISSING>'

        try:

            street_add = store.find_all('ul')[2].find_all('li')[3].text.split(',')[0]

            city = store.find_all('ul')[2].find_all('li')[3].text.split(',')[1].strip()

            state = re.search('[A-Z]{2}', store.find_all('ul')[2].find_all('li')[3].text.split(',')[2]).group(0)

            zip = re.search('\d{4,6}', store.find_all('ul')[2].find_all('li')[3].text.split(',')[2]).group(0)

            # Always comes line after state/zip
            phone = ''.join([x for x in store.find_all('ul')[2].a['href'] if x.isnumeric()])

            # hours
            hours = str([x for x in store.find_all('ul') if 'pm' in str(x)][0].find_all('p')[1]).replace('<br/>\n', '').replace('<p>', '').replace(
                '</p>', '')
            hours = hours if 'pm' in hours else '<MISSING>'

        except:

            try:

                street_add = ''.join(store.find_all('ul')[2].find_all('li')[2].text.split(',')[0:2])

                city = store.find_all('ul')[2].find_all('li')[2].text.split(',')[2].strip()

                state = re.search('[A-Z]{2}', store.find_all('ul')[2].find_all('li')[2].text.split(',')[3]).group(0)

                zip = re.search('\d{4,6}', store.find_all('ul')[2].find_all('li')[2].text.split(',')[3]).group(0)

                # Always comes line after state/zip
                phone = ''.join([x for x in store.find_all('ul')[2].a['href'] if x.isnumeric()])

                # hours
                hours = str([x for x in store.find_all('ul') if 'pm' in str(x)][0].find_all('p')[1]).replace('<br/>\n', '').replace('<p>', '').replace(
                    '</p>', '')
                hours = hours if 'pm' in hours else '<MISSING>'

            except:

                try:
                    store = pull_content(href + '/about')

                    street_add = store.h5.text.split('\n')[0].split(',')[0]

                    city = store.h5.text.split('\n')[1].split(',')[0].strip()

                    state = re.search('[A-Z]{2}', store.h5.text.split('\n')[1]).group(0)

                    zip = re.search('\d{4,6}', store.h5.text.split('\n')[1]).group(0)

                    # Always comes line after state/zip
                    phone = ''.join([x for x in store.h5.strong.text if x.isnumeric()])

                    try:

                        store = pull_content(href + '/hours')
                        # hours
                        hours = re.findall('Monday-Thursday.{1,100}.pm|Friday &amp; Saturday.{1,100}.pm|Sunday.{1,100}.pm',str(store.find_all('div',{'class':'Normal'})[0]))
                        hours = '; '.join([re.sub('\.{1,100}',' ',x).replace('amp;','') for x in hours])
                        hours = hours if 'pm' in hours else '<MISSING>'
                    except:
                        hours = '<MISSING>'
                except:
                    try:
                        store = pull_content(href + '/about')

                        street_add = store.h4.text.split('\n')[0].split(',')[0]

                        city = store.h4.text.split('\n')[1].split(',')[0].strip()

                        state = re.search('[A-Z]{2}', store.h4.text.split('\n')[1]).group(0)

                        zip = re.search('\d{4,6}', store.h4.text.split('\n')[1]).group(0)

                        # Always comes line after state/zip
                        phone = ''.join([x for x in store.h4.text.split('\n')[2] if x.isnumeric()])

                        try:

                            store = pull_content(href + '/hours')
                            # hours
                            hours = re.findall(
                                'Monday-Thursday.{1,100}.pm|Friday &amp; Saturday.{1,100}.pm|Sunday.{1,100}.pm',
                                str(store.find_all('div', {'class': 'Normal'})[0]))
                            hours = '; '.join([re.sub('\.{1,100}', ' ', x).replace('amp;', '') for x in hours])
                            hours = hours if 'pm' in hours else '<MISSING>'
                        except:
                            hours = '<MISSING>'
                    except:
                        raise AssertionError('New Website format has been developed; must update code and re-run')

        lat = '<MISSING>'
        long = '<MISSING>'



        temp_data = [

            href,

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

            hours

        ]


        logger.info(temp_data)
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

final_df = pull_info(content)

# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)