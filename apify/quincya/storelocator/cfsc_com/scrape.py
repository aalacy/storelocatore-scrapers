import csv
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="cfsc.com")


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    found_poi = []

    max_results = 50
    max_distance = 200

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for zipcode in search:
        log.info(
            "Searching: %s | Items remaining: %s" % (zipcode, search.items_remaining())
        )
        link = (
            "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=%s&location=%s&limit=%s&api_key=7620f61553e8f9aac3c03e159d2d8072&v=20181201&resolvePlaceholders=true&entityTypes=location"
            % (max_distance, zipcode, max_results)
        )

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        store_data = json.loads(base.text)["response"]["entities"]
        locator_domain = "cfsc.com"

        for store in store_data:

            try:
                page_url = store["landingPageUrl"]
            except:
                page_url = "<MISSING>"

            store_number = page_url.split("-")[-1]
            phone = store["mainPhone"]

            if phone not in found_poi:
                found_poi.append(phone)
            else:
                continue

            try:
                location_name = store["name"]
            except:
                continue

            street_address = store["address"]["line1"]
            city = store["address"]["city"]
            state = store["address"]["region"]
            zip_code = store["address"]["postalCode"]
            country_code = store["address"]["countryCode"]
            try:
                location_type = ",".join(store["services"])
            except:
                location_type = "<MISSING>"
            try:
                raw_hours = store["hours"]
                hours_of_operation = ""
                for raw_hour in raw_hours:
                    try:
                        end = raw_hours[raw_hour]["openIntervals"][0]["end"]
                        start = raw_hours[raw_hour]["openIntervals"][0]["start"]
                        hours_of_operation = (
                            hours_of_operation
                            + " "
                            + raw_hour
                            + " "
                            + start
                            + "-"
                            + end
                        ).strip()
                    except:
                        hours_of_operation = (
                            hours_of_operation + " " + raw_hour + " Closed"
                        ).strip()
            except:
                hours_of_operation = "<MISSING>"

            try:
                geo = store["geocodedCoordinate"]
            except:
                geo = store["yextDisplayCoordinate"]
            latitude = geo["latitude"]
            longitude = geo["longitude"]
            search.found_location_at(latitude, longitude)

            yield [
                    locator_domain,
                    page_url,
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
