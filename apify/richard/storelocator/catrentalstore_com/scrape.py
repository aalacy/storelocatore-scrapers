from sgrequests import SgRequests
import csv
import re

URL = "https://www.catrentalstore.com/"


def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    links = []
    stores = []
    data = []

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    # Fetch stores from location menu
    location_url = "https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&searchType=name&searchValue=Cat+Rental&maxResults=1000&productDivId=2%2C1%2C6&appId=GdeKAczdmNrGwdPo"

    stores = session.get(location_url, headers = HEADERS).json()

    for store in stores:

        # Country
        country = store["countryCode"]
        if not country in ["US","CA"]:
            continue

        # Store ID
        location_id = store["dealerLocationId"]

        # Name
        location_title = store["dealerName"]

        # Type
        try:
            location_type = re.findall(r"marketingName.+Cat Rental Store'",str(store))[0].split(":")[1].strip().replace("'","").split(", store")[0].strip().encode("ascii", "replace").decode().replace("?","-")
            if "Cat Rental Store" not in location_type:
                continue
        except:
            continue

        # Street
        street_address = (
                store["siteAddress"] + " " + store["siteAddress1"]
        ).strip()

        # State
        state = store["siteState"].replace("West Virginia","WV").replace("Washington","WA").replace("Wyoming","WY").replace("WYOMING","WY")

        # city
        city = store["siteCity"]

        # zip
        zipcode = store["sitePostal"]

        # Lat
        lat = store["latitude"]

        # Long
        lon = store["longitude"]

        # Phone
        try:
            phone = store["locationPhone"].replace("  "," ")
            if not phone:
                phone = str(store).split("phoneNumber': '")[1].split("'")[0].replace("  "," ").strip()
        except:            
            try:
                phone = str(store).split("phoneNumber': '")[1].split("'")[0].replace("  "," ").strip()
            except:
                break
                phone = "<MISSING>"

        try:
            # hour
            hour_dict = {}
            for key in store["stores"][0].keys():
                if "storeHours" in key:
                    hour_dict[key] = store["stores"][0][key]

            hour = " ".join([day + " " + hour for day, hour in hour_dict.items()]).replace("storeHours","").replace("  ", " Closed ")
            if hour[-1:] == " ":
                hour = hour + "Closed"
        except:
            hour = "<MISSING>"

        link = store["locationWebSite"]

        # Store data
        links.append(link)
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
            link,
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
        links,
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
        data.append(
            [
                URL,
                link,
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
