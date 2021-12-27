from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bocagranderestaurant_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.avera.org/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "http://bocagranderestaurant.com/contact-us/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "row tm_pb_row tm_pb_row_1"})
        loclist = str(loclist).split(
            '<div class="tm_pb_text tm_pb_module tm_pb_bg_layout_light tm_pb_text_align_center tm_pb_text_3">'
        )
        for loc in loclist:
            loc = BeautifulSoup(loc, "html.parser")
            loc = loc.get_text(separator="|", strip=True).split("|")
            location_name = loc[0]
            log.info(location_name)
            street_address = loc[1]
            address = loc[2].split(",")
            city = address[0]
            address = address[1].strip().split()
            if len(address) == 1:
                state = address[0]
                zip_postal = MISSING
            else:
                state = address[0]
                zip_postal = address[1]
            phone = loc[3]
            hours_of_operation = loc[-1]
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
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
                hours_of_operation=hours_of_operation.strip(),
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
