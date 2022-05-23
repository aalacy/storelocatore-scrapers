from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "purcelltire_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.purcelltire.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.purcelltire.com/stores/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("m035_AddNewRetailer(")[1:]
        for loc in loclist:
            loc = loc.split("')")[0].split("','")
            page_url = DOMAIN + loc[7]
            log.info(page_url)
            phone = loc[10].split(",'")[-1]
            address = loc[6]
            address = (
                BeautifulSoup(address, "html.parser")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[1]
            location_name = address[0]
            address = address[0].split(",")
            city = address[0]
            state = address[1].replace("(Mall)", "")
            zip_postal = loc[-1]
            store_number = loc[0].split(",'")[0]
            latitude = loc[1]
            longitude = loc[2]
            country_code = "US"
            hours_of_operation = (
                BeautifulSoup(loc[-2], "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
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
