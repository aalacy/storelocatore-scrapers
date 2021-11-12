from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "lundsandbyerlys_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}

DOMAIN = "https://lundsandbyerlys.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://lundsandbyerlys.com/wp-admin/admin-ajax.php?action=store_search&store_options=&autoload=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["store"]
            store_number = loc["id"]
            page_url = "https://lundsandbyerlys.com" + loc["url"]
            log.info(page_url)
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = loc["country"]
            phone = loc["phone"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            hours_of_operation = "MON - SUN " + str(loc["hours"]).replace(
                "<p>", ""
            ).replace("</p>", "")
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
                phone=phone,
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
