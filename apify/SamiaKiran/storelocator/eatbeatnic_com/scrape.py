import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "eatbeatnic_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.eatbeatnic.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.eatbeatnic.com/locations"
        r = session.get(url, headers=headers)
        loclist = json.loads(
            r.text.split('<script id="__NEXT_DATA__" type="application/json">')[
                1
            ].split("</script>")[0]
        )
        loclist = loclist["props"]["initialState"]["data"]["revenueCenters"][
            "revenueCenters"
        ]
        for loc in loclist:
            page_url = "https://www.eatbeatnic.com/locations/" + loc["slug"]
            log.info(page_url)
            address = loc["address"]
            location_name = address["cross_streets"]
            street_address = address["street"]
            city = address["city"]
            state = address["state"]
            zip_postal = address["postal_code"]
            phone = address["phone"]
            latitude = address["lat"]
            longitude = address["lng"]
            hours_of_operation = loc["hours"]["description"]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = hours_of_operation.text
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
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
