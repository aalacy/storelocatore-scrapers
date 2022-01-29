from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "whitefencefarm-il_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://whitefencefarm-il.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.whitefencefarm-il.com/carryout.php#carryout"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "carryout"})
        hours_of_operation = (
            soup.find("div", {"class": "col3"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .replace("Hours Restaurant", "")
        )
        if "Restaurant" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Restaurant")[0]
        for loc in loclist:
            loc = loc.get_text(separator="|", strip=True).split("|")
            if "(behind main restaurant)" in loc[2]:
                del loc[2]
            location_name = loc[0]
            page_url = (
                "https://www.whitefencefarm-il.com/carryout.php#"
                + location_name.split("#")[1]
            )
            log.info(location_name)
            phone = loc[-1]
            street_address = loc[1]
            address = loc[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
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
