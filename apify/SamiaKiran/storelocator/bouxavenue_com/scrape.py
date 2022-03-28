import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bouxavenue_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://bouxavenue.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.bouxavenue.com/store-locator"
        r = session.get(url, headers=headers)
        loclist = r.text.split('<script type="application/json">')[1].split(
            "</script>"
        )[0]
        loclist = json.loads(loclist)
        for loc in loclist:
            page_url = (
                "https://www.bouxavenue.com/store-locator/"
                + loc["pageIDInPageDesigner"]
            )
            log.info(page_url)
            location_name = loc["name"]
            street_address = loc["address1"] + " " + loc["address2"]
            city = loc["city"]
            if "," in city:
                city = city.split(",")[0]
            state = MISSING
            store_number = loc["id"]
            latitude = str(loc["latitude"])
            longitude = str(loc["longitude"])
            phone = loc["phone"]
            zip_postal = loc["postalCode"]
            hours_of_operation = loc["storeHours"]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = hours_of_operation.get_text(
                separator="|", strip=True
            ).replace("|", " ")
            country_code = "UK"
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
