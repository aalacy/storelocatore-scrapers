import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tropicalsmoothiecafe_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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


def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(1)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url, headers=headers, data=data)
                else:
                    r = session.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(1)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None


def fetch_data():
    address = []
    base_url = "https://locations.tropicalsmoothiecafe.com"
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        max_radius_miles=49,
        max_search_results=100,
    )
    MAX_RESULTS = 25

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        "method": "GET",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
    }

    for zipcode in search:

        result_coords = []

        r = request_wrapper(
            "https://locations.tropicalsmoothiecafe.com/search?q="
            + str(zipcode)
            + "&r="
            + str(MAX_RESULTS),
            "get",
            headers=headers,
        )
        if r is None:
            continue

        json = r.json()
        temp_locations = json["locations"]

        for locations in temp_locations:

            locator_domain = base_url
            loc = locations["loc"]
            cafe = loc["customByName"]
            location_name = cafe["Cafe Name for Reporting"]
            street_address = loc["address1"] + loc["address2"]
            city = loc["city"]
            state = loc["state"]
            zip = loc["postalCode"]
            store_number = loc["corporateCode"]
            country_code = loc["country"]
            phone = loc["phone"]
            location_type = " "
            latitude = loc["routableLatitude"]
            longitude = loc["routableLongitude"]
            result_coords.append((latitude, longitude))

            urls = loc["urls"]
            external = urls["external"]
            page_url = external["url"]

            hours = loc["hours"]
            hour_days = hours["days"]

            jk = []
            hours_of_operation = ""
            for days in hour_days:
                day = days["day"]
                day_intervals = days["intervals"]

                for intervals in day_intervals:
                    start = str(intervals["start"] // 100)
                    end = str((intervals["end"] // 100) - 12)
                jk.append(day + ":" + start + "AM" + "-" + end + "PM ")

            hours_of_operation = " ".join(jk)

            store = []
            store.append(locator_domain if locator_domain else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip if zip else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in address:
                continue
            address.append(store[2])
            yield store


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
