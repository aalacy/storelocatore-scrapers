from sgrequests import SgRequests
from geopy.geocoders import Nominatim
import csv

geolocator = Nominatim(user_agent="justsalad_com_scraper")

URL = "https://justsalad.com"

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # store data
    locations_ids = []
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    latitude_list = []
    longitude_list = []
    phone_numbers = []
    hours = []
    countries = []
    location_types = []
    locations_links = []
    data = []

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    stores = session.get('https://justsalad-admin.azurewebsites.net/v1/justsaladstores', headers=HEADERS).json()['features']

    for store in stores:

        latlon = store['geometry']

        # Lat
        lat = latlon['coordinates'][1]

        # Long
        lon = latlon['coordinates'][0]

        # Get loc info
        location = geolocator.reverse(f"{lat}, {lon}").raw

        # Country
        country = location['address']['country_code'].upper()

        if country != "US":
            continue

        if not store['properties']['locationID'][0].isalpha():
            store = store['properties']

            # Name
            location_title = store['locationName'].encode("ascii", "replace").decode().replace("?","'")

            # Store ID
            location_id = store['locationID']

            # location_link = "https://www.orderjustsalad.com/view/menu/" + store['OJSID']
            location_link = '<MISSING>'

            # Type
            location_type = '<MISSING>'

            # Street
            street_address = store['locationAddress'].replace("<br>","").replace("  "," ")

            # Phone
            phone = store['locationPhone']

            # city
            try:
                city = location['address']['city'] if 'city' in location['address'].keys() else location['address']['town']
            except:
                city = location['address']['city'] if 'city' in location['address'].keys() else location['address']['county']

            # zip
            zipcode = location['address']['postcode']

            # State
            state = location['address']['state']

            # Hour
            hour = ' '.join([store['hours1'], store['hours2'], store['hours3']])

            if hour.strip() == '':
                hour = '<MISSING>'

            # Store data
            locations_links.append(location_link)
            locations_ids.append(location_id)
            locations_titles.append(location_title)
            street_addresses.append(street_address)
            states.append(state)
            zip_codes.append(zipcode)
            hours.append(hour)
            latitude_list.append(lat)
            longitude_list.append(lon)
            phone_numbers.append(phone)
            cities.append(city)
            countries.append(country)
            location_types.append(location_type)

    for (   
            locations_link,
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            phone_number,
            latitude,
            longitude,
            hour,
            location_id,
            country,
            location_type,
    ) in zip(
        locations_links,
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        hours,
        locations_ids,
        countries,
        location_types,
    ):
        if country == "<MISSING>":
            pass
        else:
            data.append(
                [
                    URL,
                    locations_link,
                    locations_title,
                    street_address,
                    city,
                    state,
                    zipcode,
                    country,
                    location_id,
                    phone_number,
                    location_type,
                    latitude,
                    longitude,
                    hour,
                ]
            )

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
