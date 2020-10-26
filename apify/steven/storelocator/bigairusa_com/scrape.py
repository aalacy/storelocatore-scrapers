import pandas as pd
import requests as r
import os
from bs4 import BeautifulSoup as bs
import re
from lxml import etree
import sys



# Note, this is a VERY ugly code. But scraping this page is difficult because data is all over the place



# Location URL
location_url = 'https://www.bigairusa.com/'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


def pull_content(url):
    # Website requires this to grant access
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    soup = bs(r.get(url,headers=header).content,'html.parser')

    return soup


def pull_info(content):

    # list of store hrefs
    session = r.Session()
    source = session.get(location_url).text
    response = etree.HTML(source)
    # xpath for list at bottom of page. Pull all the hrefs within that. Flatten the lists of lists into 1.
    store_hrefs = [x for sublist in
                   [store.xpath('.//a/@href') for store in response.xpath('//*[@id="text-3"]/div[1]/ul')] for x in
                   sublist]
    store_data = []

    for href in store_hrefs:

        # Null out everything so doesn't get incorrectly picked up in successive loops
        city=None
        street_add=None
        city=None
        state=None
        zip=None
        store_number=None
        phone=None
        store_type=None
        lat=None
        long=None
        hours=None
        hours_cal_url=None

        # clean up the href
        href = href.replace('https://b','https://www.b')

        # Pull the data
        store = pull_content(href)

        store_type = '<MISSING>'

        store_number = '<MISSING>'

        # First check the bottom of the page for desired info
        street_raw = store.find('p', {'class': 'address'})

        # If it exists, move on
        if street_raw != None:

            # There a few different delimiters, change them all to ' I '
            street_raw = street_raw.text.replace(' • ', ' I ').replace(' | ', ' I ')

            # If address splits into more than just street address, then continue
            if len(street_raw.split(' I '))>1:

                # Pull street address
                street_add = street_raw.split(' I ')[0]

                # store name and city are the same
                city = street_raw.split(' I ')[1].split(',')[0].strip()

                # Pull State
                state = re.search('[A-Z]{2}',street_raw.split(' I ')[1].split(',')[1].strip()).group(0)

                # Extract zip code
                zip = re.search('\d{4,6}',street_raw.split(' I ')[2].strip()).group(0)

                # If phone exists, then pull
                if store.find('p',{'class':'phone'}) != None:

                    phone = ''.join([x for x in store.find('p',{'class':'phone'}).text.split(' • ')[0] if x.isnumeric()])

                else:

                    # Else try and search whole page for phone
                    try:
                        phone = re.search('\d{3}-\d{3}-\d{4}',str(store)
                                          .replace(') ','-').replace('(','')
                                          .replace('.','-')).group(0).replace('-','')
                    except:
                        # If not there, then just list as missing
                        phone = '<MISSING>'

            # If data is not in the right format at the bottom, check the top bar
            else:

                # The top bar can be on the left side
                street_raw = store.find('p', {'class': 'fusion-contact-info'})

                if street_raw == None:

                    # Or it can be right side
                    street_raw = store.find('div', {'class': 'fusion-contact-info'})

                # If it still wasn't found, kill code and investigate
                if street_raw == None:

                    print(f'address parse will not work for {href}')
                    sys.exit()

                # If it was found, move on
                else:
                    # One of these delimiters should exist
                    if (' • ' in street_raw.text) | (' | ' in street_raw.text):

                        street_raw = street_raw.text.replace(' • ', ' I ').replace(' | ', ' I ')
                        street_raw = street_raw.replace('California','CA')

                    # If it doesn't exist, then kill the code
                    else:

                        print(f'address parse will not work for {href}')
                        sys.exit()

                # Pull street address
                street_add = street_raw.split(' I ')[0]

                # store name and city are the same
                city = street_raw.split(' I ')[1].split(',')[0].strip()

                # Pull State
                state = re.search('[A-Z]{2}', street_raw.split(' I ')[1].split(',')[1].strip()).group(0)

                # Extract zip code
                zip = re.search('\d{6}', street_raw.split(' I ')[1].strip())
                zip =  zip.group(0) if zip != None else '<MISSING>'

                # Else try and search whole page for phone number
                try:
                    phone = re.search('\d{3}-\d{3}-\d{4}', str(store)
                                      .replace(') ', '-').replace('(', '')
                                      .replace('.','-')).group(0).replace('-','')
                except:
                    # If not there, then just list as missing
                    phone = '<MISSING>'


        # If the data doesn't exist at the bottom of the page, then search the top bar
        else:

            # The top bar can be left
            street_raw = store.find('p', {'class': 'fusion-contact-info'})

            if street_raw == None:
                # Or it can be right if not on right
                street_raw = store.find('div', {'class': 'fusion-contact-info'})

            # If it still wasn't found, kill code and investigate
            if street_raw == None:

                print(f'address parse will not work for {href}')
                sys.exit()

            else:
                # One of these delimiters should exist
                if (' • ' in street_raw.text) | (' | ' in street_raw.text):

                    street_raw = street_raw.text.replace(' • ', ' I ').replace(' | ', ' I ')
                    street_raw = street_raw.replace('California', 'CA')

                else:
                    # This is essentially impossible to parse. have to hard code
                    if 'Spartanburg' in street_raw.text:
                        street_raw = '660 Spartan Blvd #200 I Spartanburg, SC 29301 I (864) 580-6462'
                    else:
                        # Else kill the code
                        print(f'address parse will not work for {href}. No delimiters.')
                        sys.exit()

            # Pull street address
            street_add = street_raw.split(' I ')[0]

            # store name and city are the same
            city = street_raw.split(' I ')[1].split(',')[0].strip()

            # Pull State
            state = re.search('[A-Z]{2}', street_raw.split(' I ')[1].split(',')[1].strip()).group(0)

            # Extract zip code
            zip = re.search('\d{6}', street_raw.split(' I ')[1].strip())
            zip = zip.group(0) if zip != None else '<MISSING>'

            # Else try and search whole page
            try:
                phone = re.search('\d{3}-\d{3}-\d{4}',
                                  str(store).replace(') ', '-').replace('(', '')
                                  .replace('.', '-')).group(0).replace('-','')
            except:
                # If not there, then just list as missing
                phone = '<MISSING>'

        # Hours aren't listed, instead there is a calendar page that shows for every day
        hours = '<MISSING>'
        hours_cal_url = href + '/hours/'

        # Coordinates don't exist
        lat = '<MISSING>'
        long = '<MISSING>'


        temp_data = [

            href,

            city, #store name

            street_add,

            city,

            state,

            zip,

            'US', # Country Code

            store_number,

            phone,

            store_type,

            lat,

            long,

            hours,

            hours_cal_url
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

        'hours_of_operation',

        'hours_calendar_url'

        ]



    final_df = pd.DataFrame(store_data,columns=final_columns)



    return final_df





# Pull URL Content
content = pull_content(location_url)

# Pull all stores and info
final_df = pull_info(content)

# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)