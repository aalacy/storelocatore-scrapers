import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="firestonecompleteautocare.com")


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
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    found_poi = []

    max_results = 30

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=max_results,
    )

    log.info("Running sgzip ..")
    for postcode in search:
        base_link = (
            "https://www.firestonecompleteautocare.com/bsro/services/store/location/get-list-by-zip?zipCode=%s"
            % (postcode)
        )
        try:
            stores = session.get(base_link, headers=headers).json()["data"]["stores"]
        except:
            continue

        for store in stores:
            locator_domain = "firestonecompleteautocare.com"
            location_name = store["storeName"]
            street_address = store["address"]
            city = store["city"]
            state = store["state"]
            zip_code = store["zip"]
            country_code = "US"
            store_number = store["storeNumber"]
            if store_number in found_poi:
                continue
            found_poi.append(store_number)
            location_type = "<MISSING>"
            phone = store["phone"]

            hours_of_operation = ""
            raw_hours = store["hours"]
            for row in raw_hours:
                day = row["weekDay"]
                start = row["openTime"]
                close = row["closeTime"]
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + start + "-" + close
                ).strip()

            try:
                if store["temporarilyClosed"] == "Y":
                    hours_of_operation = "Temporarily Closed"
            except:
                pass

            latitude = store["latitude"]
            longitude = store["longitude"]
            search.found_location_at(latitude, longitude)
            link = store["localPageURL"]

            yield [
                locator_domain,
                link,
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
