import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

URL = "https://mysagedental.com/"


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
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
    page_urls = []
    data = []

    base_link = "https://mysagedental.com/wp-admin/admin-ajax.php?action=load_locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["locations"]

    for store in stores:
        # Store ID
        location_id = store["id"]

        # Type
        location_type = "<MISSING>"

        # Name
        location_title = store["title"]

        # Page url
        page_url = URL + location_title.lower().replace("east boca", "boca").replace(
            "hallandale beach", "hallandale"
        ).split("at 7")[0].strip().replace(" ", "-")

        # Street
        street_address = store["address_1"].strip()

        # city
        city_line = store["address"].strip().split(",")
        city = city_line[0].strip()

        # zip
        zipcode = city_line[-1].strip().split()[1].strip()

        # State
        state = city_line[-1].strip().split()[0].strip()

        # Phone
        phone = store["phone"]

        # Lat
        lat = store["latitude"]

        # Long
        lon = store["longitude"]
        if not lon:
            lat = "<MISSING>"
            lon = "<MISSING>"

        # Hour
        try:
            req = session.get(page_url, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hour = base.find(class_="hours").get_text(" ").strip()
        except:
            page_url = "https://mysagedental.com/find-locations/"
            hour = "<INACCESSIBLE>"

        # Country
        country = "US"

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
        page_urls.append(page_url)

    for (
        locations_title,
        page_url,
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
        page_urls,
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
                page_url,
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
