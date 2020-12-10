import csv
from sgrequests import SgRequests
import json
from sgzip import ClosestNSearch

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.rwbaird.com/' 

    search = ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()

    MAX_DISTANCE = 100

    zip_code = search.next_zip()
    dup_tracker = []
    all_store_data = []
    while zip_code:
        url = 'http://www.locatebaird.com/branch-results.htm?zipcode=' + str(zip_code)
        HEADERS = {
            'Host': 'www.locatebaird.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Length': '160',
            'Origin': 'http://www.locatebaird.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': url,
            'Cookie': 'settings={"AuthenticatedMethods":[]}; PresenterX.T=130381A5B562ADBD9A9BBDA23C23137B107AADD1145876BA2DE0780BBE53A6C7BD749573A16906814522D916848C40CC21B880B8FCCE9875EC6D6705E72EECFE3571AD34F90B29AB8A96162F7B65C8E44CA40E1DBB3C433ADCA4EB633DD4B2CE8E29DF21FFF11176FEFA1084F892BD217C75B003BC978EC7814D212C275C4E8005A613CC6F06BAD3581CC9392962C64792C0E3D4AA584EB8DB21160E4EC0AD57F3A753EB6C143AC7B00EC5311440D4AD7FD728B6; presenter=30dfa3dbca46f1a40af76941f1219685c855415d4d072409eb3e572e00fb41afe6eba520',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        
        PARAMS = {
            "Locator":"BAIRD",
            "City":"",
            "Region":"",
            "PostalCode": str(zip_code),
            "Country":"USA",
            "Company":" ",
            "ProfileTypes":"Branch",
            "DoFuzzyNameSearch":"0",
            "SearchRadius":"100"
        }
        
        COOKIES = {
            'presenter' : '30dfa3dbca46f1a40af76941f1219685c855415d4d072409eb3e572e00fb41afe6eba520',
            'PresenterX.T': '130381A5B562ADBD9A9BBDA23C23137B107AADD1145876BA2DE0780BBE53A6C7BD749573A16906814522D916848C40CC21B880B8FCCE9875EC6D6705E72EECFE3571AD34F90B29AB8A96162F7B65C8E44CA40E1DBB3C433ADCA4EB633DD4B2CE8E29DF21FFF11176FEFA1084F892BD217C75B003BC978EC7814D212C275C4E8005A613CC6F06BAD3581CC9392962C64792C0E3D4AA584EB8DB21160E4EC0AD57F3A753EB6C143AC7B00EC5311440D4AD7FD728B6',
            'settings': '{"AuthenticatedMethods":[]}'
        }
        
        r = session.post('http://www.locatebaird.com/locator/api/InternalSearch', headers=HEADERS, data=json.dumps(PARAMS), cookies=COOKIES)
        res_json = json.loads(r.content)['Results']
        if res_json == None:
            search.max_distance_update(MAX_DISTANCE)
            zip_code = search.next_zip()
            continue

        result_zips = []
        
        for loc in res_json:
            location_name = loc['Company']
            store_number = loc['ProfileId']
            if store_number not in dup_tracker:
                dup_tracker.append(store_number)
            else:
                continue
            
            street_address = loc['Address1'] + ' ' + loc['Address2'] 
            street_address = street_address.strip()
            city = loc['City']
            state = loc['Region']
            zip_code = loc['PostalCode']
            result_zips.append(zip_code)
            country_code = 'US'
            
            lat = loc['GeoLat']
            longit = loc['GeoLon']
            
            more_loc = loc['XmlData']['parameters']
            if more_loc['SiteIsLive'] == '0':
                continue
            page_url = more_loc['Url']
            if 'LocalNumber' not in more_loc:
                phone_number = more_loc['TollFreeNumber']
            else:
                phone_number = more_loc['LocalNumber']
            
            location_type = '<MISSING>'
            hours = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)

        search.max_distance_update(MAX_DISTANCE)
        zip_code = search.next_zip()

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
