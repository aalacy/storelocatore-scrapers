import json
from Scraper import Scrape
from sgrequests import SgRequests
from bs4 import BeautifulSoup

URL = "https://www.mygym.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []

    def fetch_data(self):
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

        location_url = 'https://www.mygym.com/locations'

        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        HEADERS = {'User-Agent' : user_agent}

        session = SgRequests()
        req = session.get(location_url, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        script = base.find('script', attrs={'language': "javascript"})
        js = script.text.replace('var markers =', '').replace("'", '"').strip()
        stores = json.loads(js[:-1])

        for store in stores[1:]:
            if 'coming soon' not in store['addrdisplay'].lower() and 'coming soon' not in store['name'].lower() and store['country'] in ['United States', 'Canada']:
                # Store ID
                location_id = store['placeid']

                # Name
                location_title = store['name']

                # Street
                street_address = store['addrdisplay'].strip('<br>').strip().split('<br>')[0]
                if street_address in ["N/A","NA"]:
                    street_address = '<MISSING>'

                if "(" in street_address:
                    street_address = street_address[:street_address.find("(")].strip()

                if street_address == "ST. CHARLES PLAZA":
                    street_address = "1148 Smallwood Drive"

                # Type
                location_type = 'Gym'
                if "mobile" in location_title.lower():
                    location_type = 'Mobile'
                    street_address = '<MISSING>'

                # city
                city = store['city']

                if "adjacent" in city:
                    city = city[:city.find("adjacent")].strip()

                # Country
                country = store['country']
                if country == "United States":
                    country = "US"
                else:
                    country = "CA"

                # zip
                if country == "US":
                    zipcode = store['addrmap'][-5:]
                    if "+" in zipcode:
                        zipcode = '<MISSING>'
                else:
                    zipcode = store['addrmap'][-7:].strip().replace("+"," ").upper()

                # State
                state = store['state'].replace("Maryland (MD)","MD").replace("Qu","QC")

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                if lat == 0:
                    lat = '<MISSING>'
                    lon = '<MISSING>'

                # Phone
                phone = store['phone']

                # Hour
                hour = '<MISSING>'

                # Store data
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
            self.data.append(
                [
                    self.url,
                    location_url,
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

scrape = Scraper(URL)
scrape.scrape()
