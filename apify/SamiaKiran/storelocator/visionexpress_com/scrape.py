import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "visionexpress_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://visionexpress.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.visionexpress.com/opticians"
    r = session.get(url, headers=headers)
    loclist = r.text.split('"stores":[')[1].split('],"queryParams"', 1)[0]
    loclist = "[" + loclist + "]"
    loclist = json.loads(loclist)
    for loc in loclist:
        location_name = loc["storeName"]
        latitude = loc["lat"]
        longitude = loc["lon"]
        store_number = loc["code"]
        phone = loc["Phone1"]
        city = loc["town"]
        street_address = loc["streetName"]
        state = loc["province"]
        zip_postal = loc["postalCode"]
        country_code = loc["country"]
        page_url = (
            "https://www.visionexpress.com/opticians/"
            + city.lower()
            + "/"
            + loc["slug"]
        )
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        hours_of_operation = (
            soup.find("dl", {"class": "location-opening-hours__list"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
