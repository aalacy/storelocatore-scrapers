import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "mobyskabob_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.mobyskabob.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.mobyskabob.com/wp-admin/admin-ajax.php?action=store_search&lat=38.91207&lng=-77.01902&max_results=100&search_radius=500&autoload=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            page_url = loc["permalink"]
            log.info(page_url)
            location_name = html.unescape(loc["store"])
            store_number = loc["id"]
            phone = loc["phone"]
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            city = city.split(",")
            state = city[-1]
            city = city[0]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = "US"
            latitude = loc["lat"]
            longitude = loc["lng"]
            try:
                hours_of_operation = (
                    BeautifulSoup(loc["hours"], "html.parser")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            except:
                continue
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
