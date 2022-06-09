from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "primohoagies_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://primohoagies.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://primohoagies.com/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=1&layout=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            page_url = loc["website"]
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
            hours_of_operation = loc["open_hours"]
            r = session.get(page_url, headers=headers)
            if r.status_code != 200:
                hours_of_operation = MISSING
            else:
                if "This Store is currently inactive" in r.text:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                hours_of_operation = (
                    soup.find("div", {"class": "hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("(Memorial Day) Holiday Hours", "")
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
