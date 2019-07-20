import os, csv, requests
from pdb import set_trace as bp

def xpath(hxt, query_string):
    hxp = hxt.xpath(query_string)
    if hxp:
        if hasattr(hxp[0], 'encode'):
            return hxp[0].encode('ascii', 'ignore')
        return hxp[0]
    return None

def query_params(url):
    try:
        return {obj.split('=')[0]: obj.split('=')[1].replace('+', ' ') for obj in url.split('?')[1].split('&')}
    except:
        return {}

class DataMixin(object):
    us_states = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming']
    us_states_codes = set(['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MH', 'MA', 'MI', 'FM', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY'])
    ca_provinces = ['alberta', 'british columbia', 'manitoba', 'new brunswick', 'newfoundland and labrador', 'nova scotia', 'ontario', 'prince edward island', 'quebec', 'saskatchewan']
    ca_provinces_codes = set(['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'])

    def is_us_state(self, state):
        return state in self.us_states_codes

    def is_ca_province(self, province):
        return province in self.ca_provinces_codes

    def get_geo(self, address):
        params = {'address': address, 'key': os.environ['GOOGLE_API_KEY']}
        r = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=params)
        if r.status_code == 200:
            if r.json()['results']:
                location = r.json()['results'][0]['geometry']['location']
                return location
        return None
    

class Base(DataMixin):

    csv_filename = ''
    csv_fieldnames = ['locator_domain', 'location_name', 'street_address', 'city', 'state', 'zip', 'country_code', 'store_number', 'phone', 'location_type', 'naics_code', 'latitude', 'longitude', 'hours_of_operation']
    domain_name = ''
    default_country = 'US'
    url = ''
    headers = {
        'Accept-Encoding': 'gzip, deflate, br'
        ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
        ,'Connection': 'keep-alive'
        ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    }
    rows = []

    def write_to_csv(self):
        output_file = self.csv_filename
        with open(output_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_fieldnames)
            writer.writeheader()
            for row in self.rows:
                if hasattr(self, 'map_data'):
                    row = self.map_data(row)
                writer.writerow(row)
    
    def run(self):
        self.rows = self.crawl()
        self.write_to_csv()
