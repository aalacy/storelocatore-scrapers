import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import os
import re


# Location URL
location_url = 'https://www.coxhealth.com/our-hospitals-and-clinics/our-locations/'

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
    store_hrefs = [x.a['href'] for x in content.find_all('div',{'class':'card-action'})]

    store_data = []

    for href in store_hrefs:

        store = pull_content('https://www.coxhealth.com' + href)

        store_name = re.search('>(.*)<',str(store.title)).group(0).replace('>','').replace('<','').replace('&amp;','&').split('|')[0].strip()

        store_type = '<MISSING>'

        address_split = [x.strip().replace('  ',' ') for x in str(store.find_all('div', {'class': 'module-text-block wysiwyg'})[0].p)[13:].replace('\n','').replace('</p>','').split('<br/>')]



        try:
            # determine which piece of list contains state and zip. If it doesn't exist, go to except statement
            state_city_line = [(id, x) for id, x in enumerate(address_split, 0) if re.search('[A-Z]{2} \d{4,6}',str(x))][0][0]
             
            # use state_city_line to determine which pieces of list to include
            city = address_split[state_city_line].split(', ')[0]

            street_add = ' '.join([x for x in address_split[0:state_city_line]])

            state = re.findall(' ([A-Za-z]{2}) ', address_split[state_city_line])[0].upper()

            zip = re.search('\d{4,6}', address_split[state_city_line]).group(0)

        except:

            city = '<MISSING>'

            street_add = ' '.join([x for x in address_split])

            state = '<MISSING>'

            zip = '<MISSING>'


        # Always comes after 'tel:'
        phone = re.search('tel:\d{3}-\d{3}-\d{4}', str(store).replace(' ','')).group(0)
        phone = ''.join([x for x in phone if x.isnumeric()])

        # hours
        # This is so jenky, but works
        if 'Hours<' in str(store):
            hours = re.sub('</p>|\n|<p>','', re.sub('</h4>\n<p>',' ',re.findall('Hours</h4>(.*)(?:</p>|</span><br>|</p></div><div class="modules")',str(store).replace('\xa0<span>',' ').replace('\n',''))[0])).split('<')
            # everyday & dailyVisitors is a small hack for entries that should be 
            hours = [x.strip().replace('&amp;','&').split('>')[1].split(', everyday')[0].split(' dailyVisitors')[0] if '>' in x else x.split(', everyday')[0].split(' dailyVisitors')[0].strip() for x in hours]
            hours = ' '.join([x for x in hours if (((
                ('p.m.' in x)
                or ('pm' in x)
                # Some hours refer only to psychiatry
                or ('Psychiatry' in x)
                or ('Hours' in x)
                or (('24 hours' in x) & ('7' in x)))
                & ('cafeteria' not in x) & ('Gift' not in x) & ('Call' not in x) & ('library' not in x) & ('Visitors' not in x) & ('Guidelines' not in x)))])
            hours = hours if 'pm' or 'p.m.' in hours else '<MISSING>'
            hours = re.sub(',$','',hours)
            hours = '<INACCESSIBLE>' if hours == '' else hours
            hours = 'Open 24 hours, 365 days' if 'Open 24 hours' in str(store) else hours
        else:
            hours = '<MISSING>'

         # lat long url to parse
        try:
            raw_lat_long = store.find_all('a',{'class':'btn btn01 sml rad'})[0]['href']
            lat_long_list = re.search('@(.*),', raw_lat_long).group(0).replace('@','').split(',')
            lat = lat_long_list[0]
            long = lat_long_list[1]
        except:
            lat = '<MISSING>'
            long = '<MISSING>'



        temp_data = [

            'https://www.coxhealth.com' + href,

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

soup = pull_content(location_url)

# Pull all stores and info

final_df = pull_info(soup)



# write to csv

final_df.to_csv(output_path + '/' + file_name,index=False)
