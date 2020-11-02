import csv
from sgrequests import SgRequests
import sgzip
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="famousfootwear.com")
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


def get(url, headers, attempts=1):
    global session
    if attempts == 11:
        log.debug(f"Could not get {url} after {attempts-1} attempts.")
    try:
        log.debug(f"getting {url}")
        r = session.get(url, headers=headers)
        r.raise_for_status()
        return r
    except (Exception) as ex:
        status_code = get_response_status_from_err(ex)
        if status_code == 404:
            log.debug(f"Got 404 for {url}")
            log.debug(
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            )
            return None
        log.debug(f">>> resetting session after exception getting {url} : {ex}")
        session = SgRequests()
        return get(url, headers, attempts + 1)


def get_response_status_from_err(err):
    if (
        hasattr(err, "response")
        and err.response is not None
        and hasattr(err.response, "status_code")
    ):
        return err.response.status_code
    return None


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []
    page_url = []
    countries = []
    key_set = set([])
    zip_codes = sgzip.for_radius(50)
    # headers for linux:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Host": "api.famousfootwear.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
    }

    """ headers fro windows:
    {'Sec-Fetch-User': '?1',
'Upgrade-Insecure-Requests': '1',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
    """
    for zip in zip_codes:
        log.debug(zip)
        url = (
            "https://api.famousfootwear.com/api/store/v1/storesByZip?webStoreId=20000&radius=50&zipCode="
            + str(zip)
            + "&json=true"
        )
        res = get(url, headers=headers)
        if not res:
            continue
        if "Stores" in res.json():
            stores = res.json()["Stores"]
        else:
            continue
        for store in stores:
            c = store["City"]
            s = store["State"]
            st = store["Address1"] + "," + store["Address2"]
            z = store["Zip"]
            key = c + s + st + z
            # log.debug(key)
            # log.debug(s)
            if key in key_set:
                continue
            else:
                key_set.add(key)
            page_url.append(url)
            street.append(st)
            cities.append(c)
            lat.append(store["Latitude"])
            long.append(store["Longitude"])
            locs.append(store["Name"])
            ids.append(store["Number"])
            phones.append(store["PhoneNumbers"][0]["Value"])
            states.append(s)
            days = store["StoreHoursByDay"]
            if len(days) == 14:
                days = days[::2]
            tim = ""
            for day in days:
                tim += (
                    day["Day"]
                    + ": "
                    + day["OpenTime"]
                    + " - "
                    + day["CloseTime"]
                    + ", "
                )

            timing.append(tim)
            zips.append(z)
            # log.debug(locs)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.famousfootwear.com/")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
