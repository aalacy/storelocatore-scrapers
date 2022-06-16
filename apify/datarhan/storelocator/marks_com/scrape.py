import urllib.parse

from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def make_request(session, Point):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en",
        "Accept-Encoding": "gzip, deflate, br",
        "x-web-host": "www.marks.com",
        "service-client": "mk/web",
    }
    url = "https://api.marks.com/hy/v1/marks/storelocators/near?code=&productIds=&count=20&location={}".format(
        Point[:3] + " " + Point[3:]
    )
    hdr_opt = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "service-client,x-web-host",
    }
    response = session.request(url, method="OPTIONS", headers=hdr_opt)
    response = session.get(url, headers=headers)
    if response.status_code != 200:
        return {}
    return response.json()


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
    if hoo:
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
    with SgRequests(verify_ssl=False) as session:
        search = DynamicZipSearch(
            country_codes=[SearchableCountries.CANADA],
            expected_search_radius_miles=40,
        )

        maxZ = search.items_remaining()
        for Point in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            data = make_request(session, Point)
            if "error.storelocator.find.nostores.error" not in str(data):
                if not data.get("storeLocatorPageData"):
                    continue
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
