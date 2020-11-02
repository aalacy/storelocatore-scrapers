import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import re
import os

# Location URL
location_url = 'https://www.aubonpain.com/stores/all-stores'
# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))
# file name of CSV output
file_name = 'data.csv'

# Function pull webpage content
def pull_content(url):
    # Added verify = false to stop https error
    soup = bs(r.get(url, verify=False).content,'html.parser')
    return soup

# Pull out fields and turn to dataframe
def pull_info(content):
    # Empty list for store data
    store_list = []
    # pull out store i Added verify = false to stop https errornformation
    sdata = [x for x in soup.body.find_all('div', {'class': 'loc-box text-center'})]
    # Loop through the  (such a small amount of data loop is fine)
    for store in sdata:
        # Pull Store Name
        store_name = store.find('h3',{'class':'loc-box-heading'}).text
        # Full Location - String
        store_add_str = str(store.find('dl', {'class':'forceaddressheight animated fadeIn delay1'}))
        # Pull Address
        street_add = re.findall('</dt><dd>(.*),</dd><dd>',store_add_str)[0].replace(' ',' ')
        # Pull City
        city = re.findall(',</dd><dd>(.*),',store_add_str)[0]
        # Pull State
        state = re.findall(', ([A-Z]{2}) \d{4,5}', store_add_str)[0]
        # Pull ZIP
        zip = re.findall(', [A-Z]{2} (\d{4,5})', store_add_str)[0]
        # Pull Phone
        phone = store.find('a',{'class':'phonenumber'})['href'].replace('tel:','')
        # Pull hours
        hours = re.findall('\[(.*?)\]',str(store))[0]

        # pull lat and long
        try:
            # url suffix
            href_name = store.find('a',{'class':'btn-link'})['href']
            # url
            loc_url = 'https://www.aubonpain.com' + href_name
            # pull info
            lat_long_page = pull_content(loc_url)
            lat_long = re.findall('new Microsoft.Maps.Location(.*),', str(lat_long_page))[0].replace('(','')\
                .replace(')','').split(',')
            lat = lat_long[0]
            long = lat_long[1]
        except:
            lat = '<MISSING>'
            long = '<MISSING>'

        temp_list = [location_url,
                     store_name,
                     street_add,
                     city,
                     state,
                     zip,
                     'US',
                     '<MISSING>',
                     phone,
                     '<MISSING>',
                     lat,
                     long,
                     hours]

        # fill in any nulls
        temp_list = [x.replace('','<MISSING>') if x == '' else x for x in temp_list]

        # add to holder list
        store_list = store_list + [temp_list]

    # columns for returned df
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

    # turn to df
    df = pd.DataFrame(store_list,columns=final_columns)

    return df

# Pull URL Content
soup = pull_content(location_url)

# Pull all stores and info
final_df = pull_info(soup)

# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)





