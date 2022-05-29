from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "oncueexpress_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://oncueexpress.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://oncueexpress.com/locations/"
        r = session.get(url, headers=headers)
        token = r.text.split('"nonce":"')[2].split('"')[0]
        api_url = (
            "https://oncueexpress.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce="
            + token
            + "&lang=&load_all=1&layout=1"
        )
        loclist = session.get(api_url, headers=headers).json()
        for loc in loclist:
            location_name = loc["title"]
            log.info(location_name)
            store_number = loc["id"]
            phone = loc["phone"]
            street_address = loc["street"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal_code"]
            country_code = "US"
            latitude = loc["lat"]
            longitude = loc["lng"]
            hours_of_operation = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
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
