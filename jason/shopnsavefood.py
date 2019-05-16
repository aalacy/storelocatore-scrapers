import requests
import pandas as pd
import janitor


headers = {'Content-Type': 'application/json'}
url = 'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores'
r = requests.get(url, headers=headers)

true, false, null = True, False, None


df = pd.DataFrame(r.json()['d'])
column_list = [
    'locator_domain', 'location_name', 'street_address', 'city',
    'state', 'zip', 'country_code', 'store_number', 'phone',
    'location_type', 'naics_code', 'latitude', 'longitude',
    'hours_of_operation'
]


def is_gas(row):
    """
    clean location type row to reflect fuel or store
    """
    if row:
        return 'Fuel'
    else:
        return 'Store'


def clean_phone(phone):
    """
    Remove the non-numeric characters from the phone number.
    """
    try:
        return ''.join([x for x in phone if x.isnumeric()])
    except TypeError:
        return 'NO-DATA'


# Set defaults and clean data
df['locator_domain'] = 'shopnsavefood.com'
df['country_code'] = 'NO-DATA'
df['location_type'] = 'NO-DATA'
df['naics_code'] = 'NO-DATA'
df['hours_of_operation'] = 'NO-DATA'
df['location_type'] = df['IsGasStation'].apply(is_gas)

# rename columns to the required names
df = (
    df
    .rename_column('locator_domain', 'locator_domain')
    .rename_column('Name', 'location_name')
    .rename_column('Address1', 'street_address')
    .rename_column('City', 'city')
    .rename_column('State', 'state')
    .rename_column('Zip', 'zip')
    .rename_column('country_code', 'country_code')
    .rename_column('StoreID', 'store_number')
    .rename_column('Phone', 'phone')
    .rename_column('location_type', 'location_type')
    .rename_column('naics_code', 'naics_code')
    .rename_column('Latitude', 'latitude')
    .rename_column('Longitude', 'longitude')
    .rename_column('Hours', 'hours_of_operation')
)


df['phone'] = df.phone.apply(clean_phone)
# Save data to csv file
df[column_list].to_csv('shopnsavefood_output.csv', index=False)
