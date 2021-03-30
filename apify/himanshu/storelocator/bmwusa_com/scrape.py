import csv

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="bmwusa_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    found_poi = []
    max_distance = 1000

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
    )

    for zip_code in search:
        log.info(
            "Searching: %s | Items remaining: %s" % (zip_code, search.items_remaining())
        )

        base_url = (
            "https://www.bmwusa.com/api/dealers/"
            + str(zip_code)
            + "/"
            + str(max_distance)
        )
        r = session.get(base_url, headers=headers)
        json_data = r.json()["Dealers"]
        for store_data in json_data:
            store = []
            store.append("https://www.bmwusa.com")
            store.append(store_data["DefaultService"]["Name"])
            store.append(store_data["DefaultService"]["Address"])
            store.append(store_data["DefaultService"]["City"])
            store.append(store_data["DefaultService"]["State"])
            store.append(store_data["DefaultService"]["ZipCode"])
            store.append("US")
            store.append(store_data["DefaultService"]["DealerShipUniqueID"])
            store.append(
                store_data["DefaultService"]["FormattedPhone"]
                if store_data["DefaultService"]["FormattedPhone"] != ""
                and store_data["DefaultService"]["FormattedPhone"] is not None
                else "<MISSING>"
            )
            store.append("bmw")
            latitude = store_data["DefaultService"]["LonLat"]["Lat"]
            longitude = store_data["DefaultService"]["LonLat"]["Lon"]
            store.append(latitude)
            store.append(longitude)
            search.found_location_at(latitude, longitude)
            hours = " ".join(
                list(
                    BeautifulSoup(
                        store_data["DefaultService"]["FormattedHours"], "lxml"
                    ).stripped_strings
                )
            )
            store.append(hours if hours != "" else "<MISSING>")
            link = store_data["DefaultService"]["Url"]
            if not link:
                link = "<MISSING>"
            store.append(link)
            if store[2] in found_poi:
                continue
            found_poi.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
