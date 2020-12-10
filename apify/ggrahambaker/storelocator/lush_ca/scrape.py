import csv
from sgrequests import SgRequests
from sgzip import ClosestNSearch
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    COOKIES = {
        "__cfduid":"d7fab55eb7e080a421bb2974cb2b587ca1585758329",
        "__cq_dnt":"0","cookie_hint":"1",
        "cqcid":"bczfd0ooaaJ1ZJ3391LB3RdtUg",
        "dw_dnt":"0",
        "dwac_061080d9552c65a651c9cbd0ca":"fES_TK_BnAQhG8AjWfC6kNz60pCMbMPtYVY=|dw-only|||CAD|false|Canada/Pacific|true",
        "dwanonymous_5c22f618c3a5db6093da87c48a24ff09":"bczfd0ooaaJ1ZJ3391LB3RdtUg",
        "dwsid":"quZQi_gfdf9qJm2A0shECQpYPVfbsioWKmvEyKinGrR4Aot7CUJQxCPLrDlhRsf5cYC_GL1jmhsKyoYXVNz9Lg==",
        "lush_signupModal":"\"\"",
        "sid":"fES_TK_BnAQhG8AjWfC6kNz60pCMbMPtYVY"
    }

    HEADERS = {
        'Host': 'www.lush.ca',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://www.lush.ca/en/find-a-shop',
        'Cookie': '__cfduid=d7fab55eb7e080a421bb2974cb2b587ca1585758329; dwac_061080d9552c65a651c9cbd0ca=fES_TK_BnAQhG8AjWfC6kNz60pCMbMPtYVY%3D|dw-only|||CAD|false|Canada%2FPacific|true; cqcid=bczfd0ooaaJ1ZJ3391LB3RdtUg; sid=fES_TK_BnAQhG8AjWfC6kNz60pCMbMPtYVY; dwanonymous_5c22f618c3a5db6093da87c48a24ff09=bczfd0ooaaJ1ZJ3391LB3RdtUg; __cq_dnt=0; dw_dnt=0; cookie_hint=1; dwsid=quZQi_gfdf9qJm2A0shECQpYPVfbsioWKmvEyKinGrR4Aot7CUJQxCPLrDlhRsf5cYC_GL1jmhsKyoYXVNz9Lg==; lush_signupModal=""',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'Trailers'
    }

    session = SgRequests()

    search = ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes = {'ca'})

    MAX_DISTANCE = 150

    coord = search.next_coord()
    all_store_data = []

    dup_tracker = set()
    locator_domain = 'https://www.lush.ca/'
    while coord:
        x = coord[0]
        y = coord[1]
        
        url = 'https://www.lush.ca/on/demandware.store/Sites-LushCA-Site/en_CA/Stores-FindStores?showMap=false&radius=300%20km&lat=' + str(x) + '&long=' + str(y)

        PARAMS = {
            "showMap":"false",
            "radius":"300 km",
            "lat": str(x),
            "long": str(y)
        }

        r = session.get(url, headers = HEADERS, cookies = COOKIES, params = PARAMS)
        
        res_json = json.loads(r.content)['stores']

        result_coords = []
        
        for loc in res_json:
    
            store_number = loc['ID']
            if store_number not in dup_tracker:
                dup_tracker.add(store_number)
            else:
                continue
            location_name = loc['name']
            street_address = loc['address1']
            if loc['address2'] != None:
                street_address += ' ' + loc['address2']
            
            city = loc['city']
            state = loc['stateCode']
            zip_code = loc['postalCode']
            
            lat = loc['latitude']
            longit = loc['longitude']
            
            country_code = loc['countryCode']
            
            if 'phone' not in loc:
                phone_number = '<MISSING>'
            else:
                phone_number = loc['phone']
            
            location_type = '<MISSING>'
            
            hours = '<MISSING>'
            page_url = 'https://www.lush.ca/en/shop?StoreID=' + store_number 
         
            result_coords.append((lat, longit))
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
        
        if len(res_json) == 0:
            search.max_distance_update(MAX_DISTANCE)
        else:
            search.max_count_update(result_coords)
        coord = search.next_coord()  

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
