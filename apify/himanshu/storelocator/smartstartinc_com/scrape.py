import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
prov_terr = {
    'AB': 'Alberta',
    'BC': 'British Columbia',
    'MB': 'Manitoba',
    'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador',
    'NT': 'Northwest Territories',
    'NS': 'Nova Scotia',
    'NU': 'Nunavut',
    'ON': 'Ontario',
    'PE': 'Prince Edward Island',
    'QC': 'Quebec',
    'SK': 'Saskatchewan',
    'YT': 'Yukon'
}

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    base_url = "https://www.smartstartinc.com/"

    r_token = session.get(base_url, headers=headers)
    token = r_token.text.split('ss_webapi_bearer = "')[1].split('"')[0]
    company_id = r_token.text.split('ss_api_company_id = "')[1].split('"')[0]

    # print("token === " + token)
    # print("company_id === " + company_id)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Authorization': 'Bearer ' + token,
    }

    while zip_code:
        result_coords = []

        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # print("zip_code === " + zip_code)

        locations_url = "https://webapi.smartstartinc.com/api/Shared/StoreLocations/LookupByZip" \
                        "?companyId=" + str(company_id) + "&countryISOCode=US&zipCode=" + \
                        str(zip_code) + "&limit=" + str(MAX_RESULTS)

        # print("location_url ==== " + locations_url)

        r_locations = session.get(locations_url, headers=headers)
        json_data = r_locations.json()
        # print(json.dumps(json_data,indent=4))
        current_results_len = len(json_data["Data"])  # it always need to set total len of record.
        # print("current_results_len === " + str(current_results_len))

        for script in json_data["Data"]:

            # print("script === " + str(script))

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
            raw_address = ""
            page_url = ""
            hours_of_operation = ""

            # do your logic here

            location_name = script["Name"]
            street_address = script["AddressLine1"]
            if script["AddressLine2"]:
                street_address += " " + script["AddressLine2"]
            store_number = script["StoreNumber"]
            state = script["State"]

            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(script["PostalCode"]))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(script["PostalCode"]))

            if ca_zip_list:
                zipp = ca_zip_list[0]
                country_code = "CA"

            if us_zip_list:
                zipp = us_zip_list[0]
                country_code = "US"

            city = script["City"]

            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(script["PhoneNumber"]))
            if phone_list:
                phone = phone_list[0]

            hours_of_operation = script["HoursOfOperation"]
            latitude = str(script["Latitude"])
            longitude = str(script["Longitude"])

            result_coords.append((latitude, longitude))
            if state in states:
                page_url = "https://www.smartstartinc.com/locations/" + states[state].replace(" ","-").lower() + "-" + city.replace(" ","-").lower() + "-" + street_address.replace(" ","-").lower() + "-" + zipp.replace(" ","-").lower()
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1]) + str(store[2]) not in addresses and country_code:
                addresses.append(str(store[1]) + str(store[2]))

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
