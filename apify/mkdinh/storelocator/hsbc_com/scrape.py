from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import zlib

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_co_ke")


def fetch_data():
    country = "US"
    website = "dominos.co.ke"
    url = "https://www.us.hsbc.com/content/hsbc/us/en_us/branch-locator/_jcr_content/par-tool-content/branchlocator.dpws-tools-branchlocator-data-type-branches.dpws-tools-branchlocator-data-stamp-v1-t1640284348141.cdata"
    r = session.get(url, headers=headers)

    data = json.loads(zlib.decompress(r.content))

    for item in data["branches"]:
        location_name = item["name"]
        location_type = item["Type"]

        address = item["address"]
        street_address = address["street"]
        city = address["townOrCity"]
        state = address["stateRegionCounty"]
        postal = address["postcode"]

        coord = item["coordinates"]
        lat = coord["lat"]
        lng = coord["lng"]

        phone = item["phoneNumber"]["newCustomers"]

        hours_of_operation = (
            ",".join(
                f'{day}: {hour["open"]}-{hour["close"]}'
                for day, hour in item["openingTimes"].items()
            )
            if item.get("openingTimes")
            else SgRecord.MISSING
        )

        yield SgRecord(
            locator_domain=website,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            phone=phone,
            location_type=location_type,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    data = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


if __name__ == "__main__":
    scrape()
