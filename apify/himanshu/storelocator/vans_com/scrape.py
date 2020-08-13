import csv
import urllib.parse

import sgzip
from bs4 import BeautifulSoup, Tag
from sgrequests import SgRequests

from simple_utils import *


MISSING = '<MISSING>'
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def mk_api_call(max_results: int, max_distance: int, current_zip: str, lat: float, long: float):

    xml_request = f"""
        <request><appkey>CFCAC866-ADF8-11E3-AC4F-1340B945EC6E</appkey><formdata id="locatorsearch"><dataview>store_default</dataview>
        <order>_distance</order><softmatch>1</softmatch><limit>{max_results}</limit><atleast>1</atleast><searchradius>{max_distance}
        </searchradius><geolocs><geoloc><addressline>{current_zip}</addressline><longitude>{long}</longitude><latitude>{lat}</latitude>
        </geoloc></geolocs><stateonly>1</stateonly><nobf>1</nobf><where><tnvn><eq></eq></tnvn><juliank><eq></eq></juliank><or><off><eq>TRUE</eq></off>
        <out><eq>TRUE</eq></out><aut><eq></eq></aut><offer><eq></eq></offer><offer2><eq></eq></offer2><offer3><eq></eq></offer3><name>
        <eq></eq></name><cl><eq></eq></cl><ac><eq></eq></ac><otw><eq></eq></otw><kd><eq></eq></kd><footwear><eq></eq></footwear><apparel>
        <eq></eq></apparel><snowboard_boots><eq></eq></snowboard_boots><pro_skate><eq></eq></pro_skate><surf><eq></eq></surf><justinhenry>
        <eq></eq></justinhenry><sci_fi><eq></eq></sci_fi><lottie_skate><eq></eq></lottie_skate></or></where></formdata></request>
    """.replace("\\s*\n", "")

    params = {
        "lang": "en-EN",
        "xml_request": xml_request
    }

    return session.get(url="https://locations.vans.com/01062013/where-to-get-it/ajax", params=urllib.parse.urlencode(params))

def get_hours(location: Tag) -> str:
    days_of_week_hrs = []
    for day_name, day_tag_name in [("Mon",'m'), ("Tue",'t'), ("Wed",'w'), ("Thu",'thu'), ("Fri",'f'), ("Sat",'sa'), ("Sun",'su')]:
        day_tag = location.find(day_tag_name)
        if day_tag is None or not day_tag.text.strip():
            continue
        days_of_week_hrs.append(f"{day_name}: {day_tag.text.strip()}")

    if len(days_of_week_hrs) > 0:
        return ", ".join(days_of_week_hrs)
    else:
        return MISSING

def or_missing(s: str) -> str:
    return or_else(s, MISSING)

def fetch_data():
    base_url ="https://www.vans.com/"

    encountered_identities=set()

    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['us', 'ca'])

    result_coords = []
    MAX_RESULTS = 1500
    MAX_DISTANCE = 75
    coords = search.next_coord()

    while coords:
        r = mk_api_call(max_results=MAX_RESULTS, max_distance=MAX_DISTANCE, current_zip=str(search.current_zip), lat=coords[0], long=coords[1])
        soup = BeautifulSoup(r.text, "lxml")
        data_len = len(soup.find_all('poi'))
        location = soup.find_all('poi')

        print(f"Locations found for {search.current_zip}: {len(location)}")

        for loc in location:
            country = loc.find('country').text.strip()
            if country == 'US' or country == 'CA':
                name=loc.find('name').text.strip()
                address=loc.find('address1').text.strip()
                city=loc.find('city').text.strip()
                state=loc.find('state').text.strip()
                raw_sn = loc.find('clientkey').text.strip()
                hours_of_operation = get_hours(loc)

                sn = raw_sn.split('-')
                if len(sn) == 2:
                    store_number = sn[1]
                else:
                    store_number = sn[0]
                page_url = 'https://stores.vans.com/' + state.lower() + '/' + city.lower().replace(' ','-') + '/' + raw_sn + '/'


                zip_code = loc.find('postalcode').text.strip().replace('000wa',MISSING)

                phone=loc.find('phone').text.strip().replace('T&#xe9;l.', '').replace('&#xa0;', '').replace('-', '').replace('.', '').replace(')', '').replace('(', '').replace(' ', '')


                if country=="US":
                    if len(zip_code) != 5 and zip_code != '':
                        index = 5
                        char = '-'
                        zip_code = zip_code[:index] + char + zip_code[index + 1:]

                lat=loc.find('latitude').text
                lng=loc.find('longitude').text

                # disregard duplicates (within a reasonable radius)
                identity = f"{lat[0:8]}:{lng[0:8]}"
                if identity in encountered_identities:
                    print (f"Encountered duplicate: [{identity}]; skipping.")
                    continue
                else:
                    encountered_identities.add(identity)

                result_coords.append((lat, lng))

                store=[]
                store.append(base_url)
                store.append(or_missing(remove_non_ascii(name)))
                store.append(or_missing(remove_non_ascii(address)))
                store.append(or_missing(remove_non_ascii(city)))
                store.append(or_missing(remove_non_ascii(state)))
                store.append(zip_code.replace("O","0").replace('000wa',MISSING) if zip_code.replace("O","0").replace('000wa',MISSING) else MISSING)
                store.append(or_missing(country))
                store.append(store_number if country else MISSING)
                store.append(or_missing(remove_non_ascii(phone)))
                store.append("Van Stores")
                store.append(or_missing(lat))
                store.append(or_missing(lng))
                store.append(or_missing(remove_non_ascii(hours_of_operation)))
                store.append(or_missing(page_url))

                yield store

        if data_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif data_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
