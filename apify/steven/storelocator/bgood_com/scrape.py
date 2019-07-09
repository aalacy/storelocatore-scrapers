import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import re
import os 

# Location URL
location_url = 'https://www.bgood.com/locations/'
# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))
# file name of CSV output
file_name = 'data.csv'

# Function pull webpage content in soup object
def pull_content(url):
    soup = bs(r.get(url).content,'html.parser')
    return soup

# extract data for each store
def extract_data(href_dict):
    country_store_list = []
    # loop through urls
    for url in href_dict.keys():
        # Country code associated with URL
        country_code = href_dict[url]
        # Pull a soup object of data
        data = pull_content(url)
        # Name of store -- append with BGood
        store_name = data.find_all('h1',{'class':'entry-title'})[0].text.replace(' • Menu','')


        # All location data to scrape
        location_data = str(data.find_all('div', {'class': 'wpsl-location-address'}))

        # Pull universal location fields
        city = re.findall('</span><br/><span>(.*), </span><span>', location_data)[0]
        # Handles instances of multiple breaklines off street address
        if '<span>' in city:
            city = city.split('<span>')[len(city.split('<span>')) - 1]
        street_add = re.findall('address"><span>(.*)%s' % city, location_data)[0].replace('</span><br/><span>',
                                                                                          ' ').strip()
        # Pull non canada address info
        if country_code != 'CA':
            zip = re.findall('</span><span>(\d{4,5}) </span><br/></div>', location_data)[0]
        else:
            # If it's Canada, will be alphanumeric
            zip = re.findall('</span><span>(.*) </span><br/></div>', location_data)[0].split('</span><span>')[1]

        # Pull state if US or Canada
        if country_code == 'US':
            state = re.findall('</span><span>([A-Z]{2}) </span', location_data)[0]
        elif country_code == 'CA':
            # Map canada province to a code. Have to add to dict if more provinces have stores
            state_dict = {'Ontario':'ON'}
            # Alberta
            # British
            # Columbia
            # Manitoba
            # New
            # Brunswick
            # Newfoundland and Labrador
            # Nova
            # Scotia
            # Prince
            # Edward
            # Island
            # Quebec
            # Saskatchewan
            try:
                # Pass the province through dictionary and pull code
                state = state_dict[re.findall('</span><span>(.*) </span><br/></div>', location_data)[0].split('</span><span>')[0].strip()]
            except:
                # If it fails, will have to add provience in the future
                raise AssertionError ("Canada Province/Terrority needs to be added to Canada state_dict")
        else:
            # State not applicable for other countries (?)
            state = 'N/A'
        try:
            # originally used a more sophisticated search (commented ones), but this simpler approach worked
            # Basically read out the telephone entry, then strip out any letters, but leave white space, +  and numbers
            telephone_num = ''.join(re.findall('[+ 0-9]', re.findall('div class="wpsl-contact-details"></div></div>\t\t\t\t\t\t\t(.*)<p class="hours',str(data))[0])).strip()
            # CAN/US telephone_num = re.findall('(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})<p class="',str(data))[0]
            # Switz telephone_num = re.findall('\+\d{2}[\s]\d{2}[\s]\d{3}[\s]\d{2}[\s]\d{2}',str(data))[0]
        except:
            telephone_num = None

        # Strip out hours
        try:
            # Cleaning up hours
            # No consistency to formatting. Have to remove tons of characters to get the data
            hours = re.findall('class="hours">hours:</p>(.*)pm<div class="', str(data).replace(',','').replace(' <br/>\r\n','; ').replace('<br/>\r\n','; ').replace('<br/> \r\n','; ').replace('<br/>','').replace('\r\n','; ').lower(),re.IGNORECASE)[0] + 'pm'
        except:
            try:
                hours = re.findall('class="hours">hours:</p>(.*)\t\t\t\t\t\t\t', str(data).replace(',','').replace(' <br/>\r\n','; ').replace('<br/>\r\n','; ').replace('<br/> \r\n','; ').replace('<br/>','').replace('\r\n','; ')
                                   .replace('Uhr<div ','Uhr\t\t\t\t\t\t\t<div ').lower(),re.IGNORECASE)[0]
            except:
                # There is one instance that is missed, but requires more effort than is worth
                hours = '<MISSING>'

        # List of fields to load into store list
        temp_list = [url,
                     'BGood - ' + store_name,
                     street_add,
                     city,
                     state,
                     zip,
                     country_code,
                     '<MISSING>',
                     telephone_num,
                     '<MISSING>',
                     '<MISSING>',
                     '<MISSING>',
                     hours]

        country_store_list = country_store_list + [temp_list]

    # return the string to eventually be turned into df
    return country_store_list


# pulls href data for non-us entries
def pull_non_us_hrefs(content):
    hrefs = [x['href'] for x in
     content[0].find_all('a', {'class': 'et_pb_button et_pb_button_0 et_pb_module et_pb_bg_layout_dark'})
     if ('/locations/' in x['href'])]

    return hrefs

def pull_data(content):

    # first pull out all regions
    can_content = [x for x in content.find_all('div', {'class':'state-listing international-listing'})[0] if x.h3['id']=='canada']
    germany_content = [x for x in content.find_all('div', {'class': 'state-listing international-listing'})[0] if x.h3['id'] == 'germany']
    switzerland_content = [x for x in content.find_all('div', {'class': 'state-listing international-listing'})[0] if x.h3['id'] == 'switzerland']

    # dictionary of all hrefs to their country code
    href_dict = {}
    for region in [[can_content,'CA'],
                   [germany_content,'DE'],
                   [switzerland_content,'CH']]:
        href_dict.update({k: region[1] for k in pull_non_us_hrefs(region[0])})

    # pull out all hrefs and trim down to US. US doesn't have simple filter like other countries, so have to pull everything...
    #    then filter out what already exists for other countries
    all_content = [x['href'] for x in content.find_all('a', {'class': 'et_pb_button et_pb_button_0 et_pb_module et_pb_bg_layout_dark'}) if ('/locations/' in x['href'])]
    us_content = [x for x in all_content if x not in href_dict.keys()]

    # Add US to the dictionary
    href_dict.update({k: 'US' for k in us_content})

    # extract data
    store_list = extract_data(href_dict)

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

# Extract contents and turn to df for export
final_df = pull_data(soup)

# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)
