from sgrequests import SgRequests
from sgscrape.simple_scraper_pipeline import *


session = SgRequests()

url = "https://locations.davidstea.com/"
api = "https://gannett-production.apigee.net/store-locator-next/59c135c35208bb9433f2a14c/locations-details"

def fetch_data():
    
    headers = {
    'Accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'connection': 'keep-alive',    
    'host': 'gannett-production.apigee.net',
    'if-none-match': 'W/"33e4d-iUv1vrDwV5hfR7msiVMpAASjfoc',
    'origin': 'https://locations.davidstea.com',
    'referer': 'https://locations.davidstea.com/',
    'sec-fetch-dest': '',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'x-api-key': 'iOr0sBW7MGBg8BDTPjmBOYdCthN3PdaJ',
            }
    query_params = {
        "locale": "en_US",
        "clientId": "592ec5733a5792e54eba13e1",
        "cname": "locations.davidstea.com"
            }
    r1 = session.get(api, headers = headers, params = query_params).json()

    for a in r1['features']:
        country = a['properties']['country']
        if not a['properties']['isPermanentlyClosed'] and country == "CANADA":
            yield a

def extract_hours(values) -> str:
    hours = values
    return str(hours).replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace("'", '')


def scrape():
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain= ConstantField(url),
        page_url=MappingField(mapping=['properties', 'slug'], raw_value_transform= lambda s: url + s[0]),
        location_name=MappingField(['properties', 'name']),
        latitude=MappingField(mapping=['geometry', 'coordinates'], raw_value_transform=lambda values: values[1]),
        longitude=MappingField(mapping=['geometry', 'coordinates'], raw_value_transform=lambda values: values[0]),
        street_address=MultiMappingField(mapping=[['properties', 'addressLine1'], ['properties', 'addressLine2']], multi_mapping_concat_with=', '),
        city=MappingField(['properties', 'city']),
        state=MappingField(['properties', 'province']),
        zipcode=MappingField(['properties', 'postalCode']),
        country_code=ConstantField('CA'),
        phone=MappingField(['properties', 'phoneNumber']),
        store_number=MappingField(['properties', 'branch']),
        hours_of_operation=MappingField(['properties', 'hoursOfOperation'], raw_value_transform=extract_hours),
        location_type=MappingField(['properties', 'categories'], raw_value_transform=extract_hours)
    )

    pipeline = SimpleScraperPipeline(scraper_name='davidstea.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5,
                                     post_process_filter=lambda rec: rec.location_type() != 'Corporate office')

    pipeline.run()

if __name__ == "__main__":
    scrape()
