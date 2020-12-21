import csv
import string
import random
from http import HTTPStatus
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

logger = SgLogSetup().get_logger("questdiagnostics_com")
session = SgRequests()

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


def get_random_string(stringLength=34):
    lettersAndDigits = string.ascii_lowercase + string.digits
    return "".join((random.choice(lettersAndDigits) for i in range(stringLength)))


def setCookie(current_session, domain, name, value):
    cookie = current_session.cookies.set(domain=domain, name=name, value=value)
    current_session.cookies.set_cookie(cookie)


def get_f5_cookie():
    # start with search page to populate cookies
    url_home = "https://appointment.questdiagnostics.com/patient/findlocation"
    response = session.get(url_home, headers=headers)
    for cookie in response.cookies:
        if cookie.name.startswith("f5"):
            return (cookie.name, response.cookies.get(cookie.name))


def set_session_cookies(session):
    # this request is required in order to get the "demyq" cookie, otherwise 401 unauthorized
    f5_cookie = get_f5_cookie()
    csrf_token = get_random_string()
    current_session = session.session
    setCookie(
        current_session, "appointment.questdiagnostics.com", "CSRF-TOKEN", csrf_token
    )

    if f5_cookie:
        setCookie(
            current_session,
            "appointment.questdiagnostics.com",
            f5_cookie[0],
            f5_cookie[1],
        )

    headers["X-CSRF-TOKEN"] = csrf_token
    headers["Content-Length"] = "2"
    url_encounter = (
        "https://appointment.questdiagnostics.com/mq-service/asone/encounter"
    )
    r = current_session.put(url_encounter, data="{}", headers=headers)
    r.raise_for_status()


def init_session():
    session = SgRequests()
    set_session_cookies(session)


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
MAX_DISTANCE = 300


def fetch(lat, lng, request_count, retry=0):
    payload = {
        "latitude": lat,
        "longitude": lng,
        "miles": MAX_DISTANCE,
        "maxReturn": MAX_COUNT,
        "onlyScheduled": "false",
        "questDirect": False,
        "address": {},
        "accessType": [],
        "serviceType": ["all"],
    }

    url = (
        "https://appointment.questdiagnostics.com/as-service/services/getQuestLocations"
    )

    response = session.post(url, json=payload, headers=headers, stream=True)
    request_count += 1

    if response.status_code == HTTPStatus.NO_CONTENT:
        return None

    try:
        return response.json()
    except Exception as e:
        logger.error(e)
        if retry < 3:
            fetch(lat, lng, request_count, retry + 1)

        return None


def fetch_data():
    init_session()
    request_count = 0
    dedup_tracker = []

    search = static_coordinate_list(20, SearchableCountries.USA)
    search.extend(static_coordinate_list(20, SearchableCountries.CANADA))

    for lat, lng in search:
        result_coords = []
        if request_count == 10:
            init_session()

        locations = fetch(lat, lng, request_count)
        if not locations:
            continue

        for loc in locations:
            poi = extract(loc)
            id = poi.get("store_number")

            if id not in dedup_tracker:
                dedup_tracker.append(id)
                coords = [poi.get("latitude"), poi.get("longitude")]

                result_coords.append(coords)
                yield [poi[field] for field in FIELDS]

        logger.info(
            f"locations found: {len(dedup_tracker)} | currently pulling: {len(locations)}"
        )

    logger.info(f"total locations: {len(dedup_tracker)}")


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
