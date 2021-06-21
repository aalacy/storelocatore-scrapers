import csv
import urllib.parse
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from requests.packages.urllib3.util.retry import Retry


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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


def make_request(session, Point):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "x-xsrf-token": "efe961be-c68a-44d6-a844-d18021f76f66",
    }
    url = "https://api.marks.com/hy/v1/marks/storelocators/near?code=&productIds=&count=20&location={}%2C{}".format(
        *Point
    )
    return session.get(url, headers=headers).json()


def clean_record(poi):

    store_url = [
        elem["value"] for elem in poi["urlLocalized"] if elem["locale"] == "en"
    ]
    store_url = (
        urllib.parse.urljoin("https://www.marks.com/", store_url[0])
        if store_url
        else "<MISSING>"
    )
    location_name = poi["displayName"]
    location_name = location_name if location_name else "<MISSING>"
    street_address = poi["address"]["line1"]
    if poi["address"]["line2"]:
        street_address += ", " + poi["address"]["line2"]
    street_address = street_address if street_address else "<MISSING>"
    city = poi["address"]["town"]
    city = city if city else "<MISSING>"
    state = poi["address"]["province"]
    state = state if state else "<MISSING>"
    zip_code = poi["address"]["postalCode"]
    zip_code = zip_code if zip_code else "<MISSING>"
    country_code = poi["address"]["country"]["isocode"]
    country_code = country_code if country_code else "<MISSING>"
    store_number = poi["name"]
    store_number = store_number if store_number else "<MISSING>"
    phone = poi["address"].get("phone")
    phone = phone if phone else "<MISSING>"
    location_type = ""
    location_type = location_type if location_type else "<MISSING>"
    latitude = poi["geoPoint"]["latitude"]
    latitude = latitude if latitude else "<MISSING>"
    longitude = poi["geoPoint"]["longitude"]
    longitude = longitude if longitude else "<MISSING>"
    hoo = poi.get("workingHours")
    hoo = [e.strip() for e in hoo.split()]
    hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

    cleanRecord = [
        "marks.com",  # 0
        store_url,  # 1
        location_name,  # 2
        street_address,  # 3
        city,  # 4
        state,  # 5
        zip_code,  # 6
        country_code,  # 7
        store_number,  # 8
        phone,  # 9
        location_type,  # 10
        latitude,  # 11
        longitude,  # 12
        hours_of_operation,  # 13
    ]
    return cleanRecord


def fetch_data():
    items = []
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    with SgRequests(
        retry_behavior=Retry(total=3, connect=3, read=3, backoff_factor=0.1),
        proxy_rotation_failure_threshold=0,
    ) as session:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.CANADA],
            max_radius_miles=None,
            max_search_results=20,
        )

        identities = set()
        maxZ = search.items_remaining()
        total = 0
        for Point in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            found = 0
            data = make_request(session, Point)
            recordsCount = 0
            if "error.storelocator.find.nostores.error" not in str(data):
                recordsCount = len(data["storeLocatorPageData"]["results"])
                for fullRecord in data["storeLocatorPageData"]["results"]:
                    record = clean_record(fullRecord)
                    search.found_location_at(record[11], record[12])
                    identity = str(
                        str(record[1])
                        + str(record[8])
                        + str(record[9])
                        + str(record[11])
                    )
                    if identity not in identities:
                        identities.add(identity)
                        found += 1
                        items.append(record)
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )
            total += found
            logzilla.info(
                f"{Point} | found uniques: {found}/{recordsCount} | total: {total} | progress: {progress}"
            )
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
