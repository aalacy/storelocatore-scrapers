import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="aveda.com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "Accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    addresses = []

    max_distance = 100

    search = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.CANADA,
            SearchableCountries.BRITAIN,
        ],
        max_radius_miles=max_distance,
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )
        send_data = (
            "JSONRPC=%5B%7B%22method%22%3A%22locator.doorsandevents%22%2C%22id%22%3A7%2C%22params%22%3A%5B%7B%22fields%22%3A%22DOOR_ID%2C+SALON_ID%2C+ACTUAL_DOORNAME%2C+ACTUAL_ADDRESS%2C+ACTUAL_ADDRESS2%2C+ACTUAL_CITY%2C+STORE_TYPE%2C+STATE%2C+ZIP%2C+DOORNAME%2C+ADDRESS%2C+ADDRESS2%2C+CITY%2C+STATE_OR_PROVINCE%2C+ZIP_OR_POSTAL%2C+COUNTRY%2C+PHONE1%2C+CLASSIFICATION%2C+IS_SALON%2C+IS_LIFESTYLE_SALON%2C+IS_INSTITUTE%2C+IS_FAMILY_SALON%2C+IS_CONCEPT_SALON%2C+IS_STORE%2C+HAS_EXCLUSIVE_HAIR_COLOR%2C+HAS_PURE_PRIVILEGE%2C+HAS_PERSONAL_BLENDS%2C+HAS_GIFT_CARDS%2C+HAS_PAGE%2C+HAS_SPA_SERVICES%2C+IS_GREEN_SALON%2C+HAS_RITUALS%2C+DO_NOT_REFER%2C+HAS_EVENTS%2C+LONGITUDE%2C+LATITUDE%2C+LOCATION%2C+WEBURL%2C+EMAILADDRESS%2C+APPT_URL%22%2C%22radius%22%3A%22100%22%2C%22country%22%3A%22USA%22%2C%22city%22%3A%22USA%22%2C%22region_id%22%3A%220%22%2C%22language_id%22%3A%22%22%2C%22latitude%22%3A"
            + str(lat)
            + "%2C%22longitude%22%3A"
            + str(lng)
            + "%2C%22uom%22%3A%22miles%22%2C%22primary_filter%22%3A%22filter_salon_spa_store%22%2C%22filter_HC%22%3A0%2C%22filter_PP%22%3A0%2C%22filter_SS%22%3A0%2C%22filter_SR%22%3A0%2C%22filter_EM%22%3A0%7D%5D%7D%5D"
        )
        r = session.post(
            "https://www.aveda.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents",
            headers=headers,
            data=send_data,
        )
        try:
            data = r.json()[0]["result"]["value"]["results"]
        except TypeError:
            continue

        for key in data:
            store_data = data[key]
            if store_data["COUNTRY"] not in ["USA", "Canada", "United Kingdom"]:
                continue
            store = []
            store.append("https://www.aveda.com")
            store.append(store_data["DOORNAME"])
            store.append((store_data["ADDRESS"] + " " + store_data["ADDRESS2"]).strip())
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["CITY"])
            state = store_data["STATE_OR_PROVINCE"]
            if not state:
                if "london" == store_data["CITY"].lower():
                    state = "LO"
                else:
                    state = "<MISSING>"
            store.append(state)
            store.append(store_data["ZIP_OR_POSTAL"])
            store.append(store_data["COUNTRY"])
            store.append(key)

            phone = store_data["PHONE1"]
            if phone == "" or phone is None or phone == "-":
                phone = "<MISSING>"
            if phone[-1:] == "-":
                phone = phone[:-1]
            store.append(phone)

            store.append(store_data["CLASSIFICATION"])
            latitude = store_data["LATITUDE"]
            longitude = store_data["LONGITUDE"]
            store.append(latitude)
            store.append(longitude)
            search.found_location_at(latitude, longitude)

            store.append("<INACCESSIBLE>")

            page_url = "https://www.aveda.com/locator/get_the_facts.tmpl?DOOR_ID=" + key
            store.append(page_url)

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
