from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gobblestop.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    with SgRequests(dont_retry_status_codes=([404])) as session:
        res = session.get("https://gobblestop.com/")
        soup = BeautifulSoup(res.text, "lxml")
        stores = soup.find_all("td")
        for store in stores:
            data = store.text.strip().split("\n")
            if len("".join(data)) <= 0:
                continue
            loc = data[0].split("-")[1].strip()
            id = data[0].split("#")[1].split("-")[0].strip()
            street = data[1].strip()
            sz = data[2].strip().split(",")
            city = sz[0]
            sz = sz[1].strip().split(" ")
            state = sz[0]
            zip = sz[1]
            phone = data[3].strip()

            yield SgRecord(
                locator_domain=website,
                page_url="https://gobblestop.com/",
                location_name=loc,
                street_address=street,
                city=city,
                state=state,
                zip_postal=zip,
                country_code="US",
                store_number=id,
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation="<MISSING>",
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
