import csv
from pdb import set_trace as bp

def xpath(hxt, query_string):
    hxp = hxt.xpath(query_string)
    if hxp:
        return hxp[0].encode('ascii', 'ignore')
    return None

class DataMixin(object):
    us_states = ['alabama ', 'alaska ', 'arizona ', 'arkansas ', 'california ', 'colorado ', 'connecticut ', 'delaware ', 'florida ', 'georgia ', 'hawaii ', 'idaho ', 'illinois indiana ', 'iowa ', 'kansas ', 'kentucky ', 'louisiana ', 'maine ', 'maryland ', 'massachusetts ', 'michigan ', 'minnesota ', 'mississippi ', 'missouri ', 'montana nebraska ', 'nevada ', 'new hampshire ', 'new jersey ', 'new mexico ', 'new york ', 'north carolina ', 'north dakota ', 'ohio ', 'oklahoma ', 'oregon ', 'pennsylvania rhode island ', 'south carolina ', 'south dakota ', 'tennessee ', 'texas ', 'utah ', 'vermont ', 'virginia ', 'washington ', 'west virginia ', 'wisconsin ', 'wyoming']
    ca_provinces = ['alberta', 'british columbia', 'manitoba', 'new brunswick', 'newfoundland and labrador', 'nova scotia', 'ontario', 'prince edward island', 'quebec', 'saskatchewan']

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
        output_file = 'output/%s' % self.csv_filename
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