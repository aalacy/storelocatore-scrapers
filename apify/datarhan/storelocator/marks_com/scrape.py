import urllib.parse

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from requests.packages.urllib3.util.retry import Retry
from sgscrape.sgpostal import parse_address_intl

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


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
    domain = "marks.com"
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
    addr = parse_address_intl(street_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
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

    item = SgRecord(
        locator_domain=domain,
        page_url=store_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_code,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )

    return item


def fetch_data():
    with SgRequests(
        retry_behavior=Retry(total=3, connect=3, read=3, backoff_factor=0.1),
        proxy_rotation_failure_threshold=0,
    ) as session:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.CANADA],
            expected_search_radius_miles=10,
        )

        maxZ = search.items_remaining()
        for Point in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            data = make_request(session, Point)
            if "error.storelocator.find.nostores.error" not in str(data):
                for fullRecord in data["storeLocatorPageData"]["results"]:
                    record = clean_record(fullRecord)
                    yield record


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
