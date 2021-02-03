import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

from util import Util  # noqa: I900

myutil = Util()

session = SgRequests()

start_url = "https://lavidamassage.com/locations/"
locator_domain = "https://lavidamassage.com"
base_url = "https://lavidamassage.com/wp-admin/admin-ajax.php"


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


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://lavidamassage.com",
        "Referer": "https://lavidamassage.com/locations/",
    }


def fetch_data():
    data = []
    page_url = start_url
    session.get(start_url)
    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
    new_coordinates = set()
    for lat, lng in search:
        pair = (lat, lng)
        if pair in new_coordinates:
            continue

        new_coordinates.add(pair)

        payload = {"action": "get_closest_locations", "lat": lat, "lng": lng}
        res = session.post(base_url, headers=_headers(), data=payload)
        if res.status_code != 200 or not res.json():
            new_coordinates.pop()
            continue

        for _ in res.json():
            location_name = _["title"]
            street_address, city, state, zip, country_code = myutil.parse_us_addr(
                _["location"]["address"]
            )
            store_number = "<MISSING>"
            phone = _["phone_number"]
            location_type = "<MISSING>"
            latitude = _["location"]["lat"]
            longitude = _["location"]["lng"]
            hours_of_operation = "<INACCESSIBLE>"
            _item = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            myutil._check_duplicate_by_loc(data, _item)

    if new_coordinates:
        search.mark_found(new_coordinates)
    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
