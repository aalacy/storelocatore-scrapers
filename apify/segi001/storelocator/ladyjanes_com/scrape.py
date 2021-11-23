import csv
import json

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    # Your scraper here
    locator_domain = "https://www.ladyjanes.com/"
    api = "https://www.ladyjanes.com/location/getLocationsBySearch"
    missing_string = "<MISSING>"

    s = SgRequests()
    dup_tracker = []

    search = DynamicZipSearch(country_codes=[SearchableCountries.USA])

    for postcode in search:
        p = {"search": postcode}

        locs = json.loads(s.post(api, data=p).text)["data"]["visibleLocations"]
        for loc in locs:
            st = locs[loc]
            if st["wait_time"] == "Coming Soon":
                pass
            else:
                store_name = st["api"]["name"]
                address = st["street_address"]
                state = st["state"]
                city = st["city"]
                store_zip = st["api"]["address"].strip().split(" ")[-1]
                lat = st["api"]["lat"]
                lng = st["api"]["lng"]
                search.found_location_at(lat, lng)
                store_number = st["id"]
                if store_number in dup_tracker:
                    continue
                dup_tracker.append(store_number)
                phone = st["phone"]
                hours = "Monday-Thursday : {}, Friday : {}, Saturday : {}, Sunday : {}".format(
                    st["monday_thursday"], st["friday"], st["saturday"], st["sunday"]
                )
                yield [
                    locator_domain,
                    "https://www.ladyjanes.com/locations",
                    store_name,
                    address,
                    city,
                    state,
                    store_zip,
                    "US",
                    store_number,
                    phone,
                    missing_string,
                    lat,
                    lng,
                    hours,
                ]


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
