import re
import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    url = "https://consumer.tidelaundry.com/v1/servicepoints?maxLatitude=64.93218366344629&maxLongitude=-63.19580074023439&minLatitude=14.87138826455165&minLongitude=-173.33038325976564&statuses=1&statuses=2&statuses=3"
    r = session.get(url, headers=headers)
    items = json.loads(re.sub(r'"ID\d+,', "", r.text))

    for item in items:
        locator_domain = "tidedrycleaners.com"
        store_number = item.get("id")
        page_url = f"https://tidecleaners.com/en-us/location/{store_number}"

        location_name = item.get("name")
        location_type = item.get("locationTypeId")

        address = item.get("address", {})
        street_address = address.get("streetLine1")
        if address.get("streetLine2"):
            street_address += f', {address.get("streetLine2")}'

        city = address.get("city")
        state = address.get("state")
        postal = address.get("zipCode")
        country_code = "US"

        latitude = address.get("latitude")
        longitude = address.get("longitude")

        phone = item.get("phoneNumber")
        hours_of_operations = ", ".join(
            f'{weekdays[item["weekday"]]}: {item["opensLocal"]}-{item["closesLocal"]}'
            for item in item["hoursOfOperation"]
        )

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            store_number=store_number,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            hours_of_operation=hours_of_operations,
        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
