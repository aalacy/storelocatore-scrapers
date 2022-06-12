import re
from urllib.parse import urljoin

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    start_url = "https://www.redlion.com/locations"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    session = SgRequests()
    data = session.get(
        "https://www.redlion.com/page-data/locations/page-data.json"
    ).json()
    static_hashes = data["staticQueryHashes"]

    for hash in static_hashes:
        response = session.get(
            f"https://www.redlion.com/page-data/sq/d/{hash}.json"
        ).json()
        data = response["data"]
        all_hotels = data.get("allHotel")
        if not all_hotels:
            continue

        all_locations = all_hotels["nodes"]

    for poi in all_locations:
        store_url = urljoin(start_url, poi["path"]["alias"])
        poi = session.get(
            f'https://www.redlion.com/page-data{poi["path"]["alias"]}/page-data.json'
        ).json()
        poi = poi["result"]["data"]["hotel"]

        location_name = poi["name"]
        if "TEST DO" in location_name.upper():
            continue
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["address_line1"]
        if poi["address"].get("address_line2"):
            street_address += " " + poi["address"]["address_line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["locality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["administrative_area"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country_code"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        try:
            latitude = poi["lat_lon"]["lat"]
            longitude = poi["lat_lon"]["lon"]
        except:
            latitude = ""
            longitude = ""
        hours_of_operation = "<MISSING>"

        sgw.write_row(
            SgRecord(
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
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
