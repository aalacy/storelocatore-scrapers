import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "anchor_org_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://anchor.org.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        count = 0
        total_count = "https://www.anchor.org.uk/internals/property-finder/search"
        total_count = session.get(total_count, headers=headers).json()["total_count"]
        while count <= int(total_count):
            url = (
                "https://www.anchor.org.uk/internals/property-finder/search?offset="
                + str(count)
            )
            loclist = session.get(url, headers=headers).json()["results"]
            count = count + 12
            for loc in loclist:
                loc = json.loads(loc)
                temp = loc["metatag"]["value"]
                location_name = temp["og_title"]
                page_url = temp["canonical_url"].replace("\\/", "/")
                try:
                    location_type = loc["service_details"]["AH"]["title"]
                except:
                    try:
                        location_type = loc["service_details"]["ARH"]["title"]
                    except:
                        location_type = loc["service_details"]["GMS"]["title"]
                if "Care homes" in location_type:
                    continue
                log.info(page_url)
                try:
                    street_address = (
                        loc["field_feed_address_1"][0]["value"]
                        + " "
                        + loc["field_feed_address_2"][0]["value"]
                    )
                except:
                    street_address = loc["field_feed_address_1"][0]["value"]
                if street_address == ".":
                    street_address = location_name
                city = loc["field_feed_town"][0]["value"]
                try:
                    state = loc["field_feed_county"][0]["value"]
                except:
                    state = MISSING
                zip_postal = loc["field_feed_postcode"][0]["value"]
                country_code = "UK"
                latitude = loc["field_feed_latitude"][0]["value"]
                longitude = loc["field_feed_longitude"][0]["value"]
                try:
                    phone = loc["field_feed_telephone"][0]["value"]
                except:
                    phone = MISSING
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=MISSING,
                )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
