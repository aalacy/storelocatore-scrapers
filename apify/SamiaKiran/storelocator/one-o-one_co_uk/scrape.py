from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "one-o-one_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://one-o-one.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://one-o-one.co.uk/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=5802e450e2&load_all=1&layout=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            page_url = loc["website"]
            if not page_url:
                page_url = "https://one-o-one.co.uk/our-stores/"
            log.info(page_url)
            location_name = loc["title"]
            store_number = loc["id"]
            phone = loc["phone"]
            street_address = loc["street"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal_code"]
            country_code = "US"
            latitude = loc["lat"]
            longitude = loc["lng"]
            hours_of_operation = (
                str(loc["open_hours"])
                .replace('":["', " ")
                .replace('"],"', " ")
                .replace('{"', "")
                .replace('"]}', "")
            )
            if (
                'mon":"0","tue":"0","wed":"0","thu":"0","fri":"0","sat":"0","sun":"0"'
                in hours_of_operation
            ):
                hours_of_operation = MISSING
            country_code = loc["country"]
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
