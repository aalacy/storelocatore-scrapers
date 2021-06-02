import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}
    session = SgRequests()

    base_link = "https://russellcellular.com/wp-admin/admin-ajax.php"
    locator_domain = "russellcellular.com"

    found_poi = []

    max_results = 3
    max_distance = 100

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for lat, lng in search:

        # Request post
        payload = {"action": "localpages", "lat": lat, "lon": lng}

        response = session.post(base_link, headers=headers, data=payload)
        base = BeautifulSoup(response.text, "lxml")

        items = base.find_all("div", attrs={"style": "display:none"})
        for item in items:
            location_name = item.strong.text.strip()
            if "soon" in location_name.lower():
                continue

            try:
                geo = json.loads(item["data-gmapping"])
                latitude = geo["latlng"]["lat"]
                longitude = geo["latlng"]["lng"]
                search.found_location_at(latitude, longitude)
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            raw_address = str(item.find(class_="infobox")).split("<br/>")[1:-2]
            street_address = " ".join(raw_address[:-1]).strip()
            if "{" in street_address:
                street_address = street_address[: street_address.find("{")].strip()
            if street_address in found_poi:
                continue
            found_poi.append(street_address)
            city_line = raw_address[-1].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = item.a.text.strip()
            hours_of_operation = "<MISSING>"

            yield [
                locator_domain,
                base_link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
