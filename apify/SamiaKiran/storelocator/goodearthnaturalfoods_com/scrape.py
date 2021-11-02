from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "goodearthnaturalfoods_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://goodearthmarkets.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://goodearthmarkets.com/locations/"
        r = session.get(url, headers=headers)
        loclist = r.text.split('<div class="mcb-wrap-inner">')[2:-1]
        for loc in loclist:
            loc = BeautifulSoup(loc, "html.parser")
            address = loc.get_text(separator="|", strip=True).split("|")
            phone = address[3]
            location_name = address[0]
            log.info(location_name)
            street_address = address[1]
            address = address[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
            temp = loc.findAll("div", {"class": "column_attr"})
            hours_of_operation = (
                temp[1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Store Hours: -", "")
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
