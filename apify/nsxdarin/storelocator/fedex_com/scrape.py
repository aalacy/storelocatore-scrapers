import csv
from typing import Dict, Callable
import bs4
import urllib
from sgscrape import simple_network_utils
from sgscrape import simple_utils
import sglogging
from sgscrape.eta import ETA

log = sglogging.SgLogSetup().get_logger('fedex.com')

MISSING = '<MISSING>'
SEARCH_API_DOMAIN = 'https://6-dot-fedexlocationstaging-1076.appspot.com'
DOMAIN = 'https://local.fedex.com'

usa = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
       "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
       "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
       "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
       "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
canada = ['NF', 'NS', 'PE', 'NB', 'SK', 'ON', 'QC', 'PQ', 'YK', 'NT', 'NU', 'AB']

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        header_row = simple_utils.sorted_keys(simple_utils.sg_record())
        writer.writerow(header_row)
        for row in data:
            if row:
                writer.writerow(row)

def page_url_from_id(id: str) -> str:
    quoted_loc_id = urllib.parse.quote_plus(f'["{id}"]')
    return f'{DOMAIN}/en-us/info-window/?locids={quoted_loc_id}'

def parse_body(location_id, lat, lng, body_xml) -> Dict[str, str]:
    address = body_xml.find('div', {'class':'loc-infowin-address'}).text.split('\t')
    address = [el.strip() for el in address if el.strip()]

    city_state_zip = address[-1].strip().split(',')

    if len(address) > 2:
        location_type = address[0]
        street_address = ', '.join(address[1:-1])
    else:
        location_title_el = body_xml.find('a', {'class': 'loc-item-title'})
        location_type = location_title_el.text if location_title_el else MISSING
        street_address = address[0]

    city = city_state_zip[0]
    state_zip = [el for el in city_state_zip[1].split(' ') if el.strip()]

    # this happens in other territories, e.g. Bermuda
    if len(state_zip) != 2:
        return simple_utils.sg_record() # return an empty record.

    state = state_zip[0]
    zipcode = state_zip[1]

    loc_name_el = body_xml.find('a', {'class':'loc-item-title'})

    if state.upper() in usa:
        country_code = 'us'
    elif state.upper() in canada:
        country_code = 'ca'
    else:
        country_code = MISSING

    hours_elements = [div for div in body_xml.find_all('div', {'class':'day'}) if len(div.attrs['class']) == 1]
    hours_of_operation = ''
    for hours_el in hours_elements:
        hours_for_day = hours_el.text
        hours_of_operation += hours_for_day + ', '
    hours_of_operation = hours_of_operation.rstrip(', ').replace('\n', ' ')

    return simple_utils.sg_record(
        page_url= page_url_from_id(location_id),
        location_name=loc_name_el.text if loc_name_el else MISSING,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zipcode,
        country_code=country_code,
        store_number=location_id,
        phone=MISSING,
        location_type=location_type,
        latitude=lat,
        longitude=lng,
        locator_domain=DOMAIN,
        hours_of_operation=hours_of_operation
    )

def fetch_data():

    coords = [(-73.9859414, 40.7135097),
              (-120.9859414, 40.7135097),
              (-157.9859414, 20.7135097),
              (-105.9859414, 40.7135097),
              (-157.9859414, 55.7135097)]

    loc_ids = set()
    locs = []

    log.debug('Fetching location list...')

    for lng, lat in coords:
        data = simple_network_utils.fetch_json(request_url=f'{SEARCH_API_DOMAIN}/rest/search/stores?&projectId=13284125696592996852&where=ST_DISTANCE(geometry%2C+ST_POINT({lng}%2C+{lat}))%3C1609000&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=list&select=geometry%2C+LOC_ID%2C+PROMOTION_ID%2C+SEQUENCE_ID%2CST_DISTANCE(geometry%2C+ST_POINT(-73.9859414%2C+40.7135097))as+distance&orderBy=distance+ASC&limit=100000&maxResults=100000&_=1566253089266',
                                               headers= {
                                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                                                'Connection':'Keep-Alive'
                                               },
                                               query_params={})[0]

        for feature in data['features']:
            loc_id = feature['properties']['LOC_ID']
            if loc_id in loc_ids:
                continue
            else:
                loc_ids.add(loc_id)
                lat = feature['geometry']['coordinates'][1]
                lng = feature['geometry']['coordinates'][0]
                locs.append((loc_id, lat, lng))

    log.debug(f'Fetching and processing {len(locs)} in parallel...')

    eta = ETA(total_record_count=len(locs))
    eta.kickoff()
    for idx, loc_tuple in enumerate(locs):
        if idx and idx % 100 == 0:
            log.debug(eta.stringify_stats(eta.update_and_get_stats(100)))

        yield get_location(loc_tuple)

def get_location(loc_tuple: (int, float, float)):
    loc, lat, lng = loc_tuple

    location_parser: Callable[[bs4.Tag], Dict[str, str]] = \
        lambda tag: parse_body(loc, lat, lng, tag)

    try:
        parsed_locs = simple_network_utils.fetch_xml(request_url=f'{DOMAIN}/en-us/info-window/',
                                                     query_params={'locids': f'["{loc}"]'},
                                                     root_node_name='html',
                                                     location_node_name='body',
                                                     location_parser=location_parser)

        parsed_loc = list(parsed_locs)[0]
        if parsed_loc['country_code'] != MISSING:
            return simple_utils.sort_values_dict(parsed_loc)
        else:
            return None

    except Exception as e:
        log.error(f'Error: [{e}] in: {page_url_from_id(loc)}')
        raise e

def scrape():
    data = fetch_data()
    write_output(data)

if __name__ == "__main__":
    scrape()
