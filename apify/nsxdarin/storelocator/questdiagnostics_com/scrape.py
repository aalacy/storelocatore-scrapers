import csv
import string
import random
import threading
from http import HTTPStatus
from sglogging import SgLogSetup
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("questdiagnostics_com")
local = threading.local()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}

FIELDS = [
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


def get_session():
    if not hasattr(local, "session") or local.request_count == 10:
        local.session = SgRequests()
        local.request_count = 0
        set_session_cookies(local.session)

    return local.session


def get_random_string(stringLength=34):
    lettersAndDigits = string.ascii_lowercase + string.digits
    return "".join((random.choice(lettersAndDigits) for i in range(stringLength)))


def setCookie(current_session, domain, name, value):
    cookie = current_session.cookies.set(domain=domain, name=name, value=value)
    current_session.cookies.set_cookie(cookie)


def set_session_cookies(session):
    # this request is required in order to get the "demyq" cookie, otherwise 401 unauthorized
    csrf_token = get_random_string()
    current_session = session.get_session()
    setCookie(
        current_session, "appointment.questdiagnostics.com", "CSRF-TOKEN", csrf_token
    )

    headers["X-CSRF-TOKEN"] = csrf_token
    headers["Content-Length"] = "125"
    url_encounter = (
        "https://appointment.questdiagnostics.com/mq-service/asone/encounter"
    )

    session.put(url_encounter, data="{}", headers=headers)
    session.get(
        "https://appointment.questdiagnostics.com/as-service/services/redirectBeta"
    )
    session.get(
        "https://appointment.questdiagnostics.com/as-service/services/maintenance"
    )
    session.get("https://appointment.questdiagnostics.com/mq-service/session/user")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


def extract(loc):
    name = loc["name"]
    address = loc["address"]
    if loc["address2"]:
        address = f"{address}, {loc['address2']}"
    city = loc["city"]
    state = loc["state"]
    postal = loc["zip"]
    phone = loc["phone"]
    store_num = loc["siteCode"]
    hours = loc["hoursOfOperations"]
    if "; Drug" in hours:
        hours = hours.split("; Drug")[0]
    if "Sa" not in hours:
        hours = hours + "; Sa: Closed"
    if "Sun" not in hours:
        hours = hours + "; Su: Closed"
    lat = loc["latitude"]
    lng = loc["longitude"]

    typ = loc["locationType"]
    if typ == " ":
        typ = "<MISSING>"
    country = "US"

    return {
        "locator_domain": "questdiagnostics.com",
        "store_number": store_num,
        "location_name": name,
        "street_address": address,
        "city": city,
        "state": state,
        "zip": postal,
        "country_code": country,
        "latitude": lat,
        "longitude": lng,
        "phone": phone,
        "hours_of_operation": hours,
        "location_type": "<MISSING>",
        "page_url": "<MISSING>",
    }


MAX_COUNT = 1500
MAX_DISTANCE = 100


@retry(stop=stop_after_attempt(3))
def fetch(lat, lng):
    payload = {
        "miles": MAX_DISTANCE,
        "address": {},
        "latitude": lat,
        "longitude": lng,
        "maxReturn": MAX_COUNT,
        "onlyScheduled": "false",
        "accessType": [],
    }

    url = (
        "https://appointment.questdiagnostics.com/as-service/services/getQuestLocations"
    )

    response = get_session().post(
        url, json=payload, headers=headers, stream=True, timeout=15
    )
    local.request_count += 1

    if response.status_code == HTTPStatus.NO_CONTENT:
        return None

    return response.json()


def fetch_data():
    completed = 0
    dedup_tracker = []

    search = static_coordinate_list(100, SearchableCountries.USA)
    search += static_coordinate_list(30, SearchableCountries.CANADA)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch, lat, lng) for lat, lng in search]

        for future in as_completed(futures):
            completed += 1
            try:
                locations = future.result()

                if not locations:
                    continue

                for loc in locations:
                    poi = extract(loc)
                    id = poi.get("store_number")

                    if id not in dedup_tracker:
                        dedup_tracker.append(id)
                        yield [poi[field] for field in FIELDS]

                logger.info(
                    f"locations found: {len(dedup_tracker)} | currently pulling: {len(locations)} | remaining postals: {completed}/{len(search)}"
                )
            except:
                pass

    logger.info(f"total locations: {len(dedup_tracker)}")


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
