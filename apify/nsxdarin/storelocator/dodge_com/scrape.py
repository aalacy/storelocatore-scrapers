import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.static import static_zipcode_list
from sgzip.dynamic import SearchableCountries
from tenacity import retry, stop_after_attempt

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dodge_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def parse_hours(json_hours):
    days = [
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    ]
    hours = []
    for day in days:
        if json_hours[day]["closed"]:
            hours.append(f"{day}: closed")
        else:
            open_time = (
                json_hours[day]["open"]["time"] + " " + json_hours[day]["open"]["ampm"]
            )
            close_time = (
                json_hours[day]["close"]["time"]
                + " "
                + json_hours[day]["close"]["ampm"]
            )
            hours.append(f"{day}: {open_time}-{close_time}")
    return ", ".join(hours)


def handle_missing(x):
    if not x:
        return "<MISSING>"
    return x


@retry(stop=stop_after_attempt(5))
def get_url(url):
    session = SgRequests()
    return session.get(url, headers=headers).json()


def fetch_data():
    ids = set()
    codes = static_zipcode_list(radius=50, country_code=SearchableCountries.USA)
    for code in codes:
        logger.info("Pulling Zip Code %s..." % code)
        url = (
            "https://www.dodge.com/bdlws/MDLSDealerLocator?brandCode=D&func=SALES&radius=50&resultsPage=1&resultsPerPage=100&zipCode="
            + code
        )
        r = get_url(url)
        if "error" in r:
            continue
        dealers = r["dealer"]
        logger.info(f"found {len(dealers)} dealers")
        for dealer in dealers:
            store_number = handle_missing(dealer["dealerCode"])
            if store_number in ids:
                continue
            else:
                ids.add(store_number)
            website = "dodge.com"
            typ = "<MISSING>"
            name = handle_missing(dealer["dealerName"])
            country = handle_missing(dealer["dealerShowroomCountry"])
            add = handle_missing(dealer["dealerAddress1"])
            add2 = dealer["dealerAddress2"]
            if add2:
                add = f"add {add2}"
            state = handle_missing(dealer["dealerState"])
            city = handle_missing(dealer["dealerCity"])
            zc = handle_missing(dealer["dealerZipCode"][0:5])
            purl = handle_missing(dealer["website"])
            phone = handle_missing(dealer["phoneNumber"])
            lat = handle_missing(dealer["dealerShowroomLatitude"])
            lng = handle_missing(dealer["dealerShowroomLongitude"])
            hours = parse_hours(dealer["departments"]["sales"]["hours"])
            yield [
                website,
                purl,
                name,
                add,
                city,
                state,
                zc,
                country,
                store_number,
                phone,
                typ,
                lat,
                lng,
                hours,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
