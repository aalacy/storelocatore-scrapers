import csv
from sglogging import sglog
from sgrequests import SgRequests

from sgscrape.pause_resume import CrawlState
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
identities = set()


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


def record_transformer(poi):
    DOMAIN = "zara.com"
    store_url = "<MISSING>"
    location_name = poi["addressLines"][0]
    street_address = poi["addressLines"][0]
    city = poi["city"]
    city = city if city else "<MISSING>"
    state = poi.get("state")
    state = state if state else "<MISSING>"
    zip_code = poi["zipCode"]
    zip_code = zip_code if zip_code else "<MISSING>"
    country_code = poi["countryCode"]
    store_number = poi["id"]
    phone = poi["phones"]
    phone = phone[0] if phone else "<MISSING>"
    location_type = poi["datatype"]
    latitude = poi["latitude"]
    latitude = latitude if latitude else "<MISSING>"
    longitude = poi["longitude"]
    longitude = longitude if longitude else "<MISSING>"
    hours_of_operation = "<MISSING>"

    item = [
        DOMAIN,
        store_url,
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
    return (item, latitude, longitude)


def search_all(session, search, hdr):
    total = 0
    maxZ = search.items_remaining()

    def getPoint(point, session, hdr):
        url = "https://www.zara.com/{}/en/stores-locator/search?lat={}&lng={}&isGlobalSearch=true&showOnlyPickup=false&isDonationOnly=false&ajax=true".format(
            search.current_country(), *point
        )
        data = session.get(url, headers=hdr)
        return data.json()

    for Point in search:
        found = 0
        for poi in getPoint(Point, session, hdr):
            record, foundLat, foundLng = record_transformer(poi)
            search.found_location_at(foundLat, foundLng)
            if str(record) not in identities:
                identities.add(str(record))
                found += 1
                yield record
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logzilla.info(
            f"{str(Point).replace('(','').replace(')','')}|found: {found}|total: {total}|prog: {progress}|\nRemaining: {search.items_remaining()} Searchable: {search.current_country()}"
        )


def fetch_data():
    # Your scraper here
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    }
    with SgRequests() as session:
        search = DynamicGeoSearch(
            country_codes=SearchableCountries.ALL, max_radius_miles=30
        )
        for item in search_all(session, search, hdr):
            yield item


def scrape():
    data = []
    for item in fetch_data():
        data.append(item)
    write_output(data)


if __name__ == "__main__":
    scrape()
