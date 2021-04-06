import csv
import html
from typing import Dict, NamedTuple

import lxml.html
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

DOMAIN = "happynails.com"
URL = "https://www.happynails.com/store-locator/"

API_URL = "https://www.happynails.com/wp-admin/admin-ajax.php"

_logger = SgLogSetup().get_logger("happynails_com")


class Row(NamedTuple):
    locator_domain: str
    page_url: str
    location_name: str
    street_address: str
    city: str
    state: str
    zip: str
    country_code: str
    store_number: str
    phone: str
    location_type: str
    latitude: str
    longitude: str
    hours_of_operation: str


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(Row._fields)

        # Body
        for row in data:
            writer.writerow(row)


def _transform_hours(hours: str) -> str:
    def _transform_day(tr):
        day, hours = tr.xpath("td")
        return f"{day.text}: {hours.xpath('time')[0].text}"

    hours_html = lxml.html.document_fromstring(hours)
    return r"; ".join(_transform_day(day) for day in hours_html.xpath("//tr"))


def _missing_if_empty(value: str):
    return value if value else "<MISSING>"


def _parse_row(data: Dict[str, str]) -> Row:

    return Row(
        locator_domain=DOMAIN,
        page_url=URL,
        location_name=html.unescape(data["store"]),
        street_address=data["address"],
        city=data["city"],
        state=_missing_if_empty(data["state"]),
        zip=_missing_if_empty(data["zip"]),
        country_code=data["country"],
        store_number=data["id"],
        phone=data["phone"],
        location_type="<MISSING>",
        latitude=data["lat"],
        longitude=data["lng"],
        hours_of_operation=_transform_hours(data["hours"]),
    )


def _query_url(**kwargs: str) -> str:
    query = "&".join(f"{k}={v}" for k, v in kwargs.items())
    if not kwargs:
        return API_URL
    return f"{API_URL}?{query}"


def fetch_data():

    session = SgRequests()
    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])

    all_rows = set()
    for lat, lng in search:
        _logger.info("(%f, %f) | remaining: %d", lat, lng, search.items_remaining())

        # NOTE: `autoload=1` enables "closest N" search behavior with N=25
        url = _query_url(action="store_search", lat=lat, lng=lng, autoload=1)

        response = session.get(url)
        rows = [_parse_row(r) for r in response.json()]
        all_rows.update(rows)

        for r in rows:
            search.found_location_at(r.latitude, r.longitude)

    return all_rows


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
