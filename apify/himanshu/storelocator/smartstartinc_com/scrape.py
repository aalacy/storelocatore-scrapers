import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('smartstartinc_com')





session = SgRequests()

def write_output(data):
    with open('smartstartinc_com.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=["US"])
    MAX_RESULTS = 500
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    base_url = "https://www.smartstartinc.com/"

    r_token = session.get(base_url, headers=headers)
    token = r_token.text.split("ss_webapi_bearer = '")[1].split("'")[0]
    company_id = r_token.text.split("ss_api_company_id = '")[1].split("'")[0]


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Authorization': 'Bearer ' + token,
    }

    while zip_code:
        result_coords = []

        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))

        locations_url = "https://webapi.smartstartinc.com/api/Shared/StoreLocations/LookupByZip" \
                        "?companyId=" + str(company_id) + "&countryISOCode=US&zipCode=" + \
                        str(zip_code) + "&limit=100"


        json_data = session.get(locations_url, headers=headers).json()
        
        current_results_len = len(json_data["Data"])  
        

        for script in json_data["Data"]:

            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = ""
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            page_url = ""
            hours_of_operation = ""

            location_name = script["Name"]
            street_address = script["AddressLine1"]
            if script["AddressLine2"]:
                street_address += " " + script["AddressLine2"]
            store_number = script["StoreNumber"]
            state = script["State"]
            city = script["City"]
            phone = script["WebPhoneNumber"]

            if script["HoursOfOperation"]:
                hours_of_operation = re.sub(r'\s+'," ",script["HoursOfOperation"])
            latitude = str(script["Latitude"])
            longitude = str(script["Longitude"])

            result_coords.append((latitude, longitude))
            if state in states:
                zipp = script['PostalCode']     
                page_url = "https://www.smartstartinc.com/locations/" + states[state].replace(" ","-").lower() + "-" + city.replace(" ","-").lower() + "-" + street_address.replace(" ","-").lower() + "-" + zipp.replace(" ","-").lower()
                country_code = "US"      
            else:
                continue
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1]) + str(store[2]) not in addresses and country_code:
                addresses.append(str(store[1]) + str(store[2]))

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store

        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()

   





       

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
