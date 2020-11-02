import pandas as pd
import requests as r
import os


# Location URL
location_url = 'https://saladworks.com/api/locations?mealperiodId=58&orderChannelId=55'

# output path of CSV
output_path = os.path.dirname(os.path.realpath(__file__))

# file name of CSV output
file_name = 'data.csv'


# Function pull webpage content
def pull_content(url):
    soup = r.get(url).json()
    return soup


def pull_info(content):

    # list of store hrefs
    stores = [x for x in content['Locations']]

    store_data = []

    for store in stores:

        # some of these json strings are empty
        if store['City']:

            street_add = store['Address'].title()
            street_add = '<MISSING>' if store['Address'] == '' else store['Address']

            store_name = 'Saladworks'

            try:
                store_type = store['@type']
            except:
                store_type = '<MISSING>'

            store_num = store['LocationID']

            city = store['City'].title()
            city = '<MISSING>' if store['City'] == '' else store['City']

            state = store['State']
            state = '<MISSING>' if store['State'] == '' else store['State']

            zip = store['PostalCode']
            zip = '<MISSING>' if store['PostalCode'] == '' else store['PostalCode']

            phone = ''.join([x for x in store['Phone'] if x.isnumeric()])

            hours = '<MISSING>'

            lat = store['Latitude']
            long = store['Longitude']



            temp_data = [

                location_url,

                store_name,

                street_add,

                city,

                state,

                zip,

                'US',

                store_num,

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
content = pull_content(location_url)

# Pull all stores and info
final_df = pull_info(content)

# write to csv
final_df.to_csv(output_path + '/' + file_name,index=False)