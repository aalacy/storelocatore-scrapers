from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "applestorage_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://applestorage.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://inventory.g5marketingcloud.com/api/v3/client_search_data?client_urns=g5-c-5h4clywzg-apple-self-self-storage-client"
        log.info("Fetching Clients Id...")
        r = session.get(url, headers=headers)
        client_id = r.text.split('"client_id":[')[1].split("]")[0]
        url = (
            "https://inventory.g5marketingcloud.com/api/v1/locations?client_id="
            + client_id
            + "&per_page=100"
        )
        loclist = session.get(url, headers=headers).json()["locations"]
        for loc in loclist:
            page_url = loc["website_page_prefix"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = loc["name"]
            store_number = str(loc["id"])
            phone = loc["phone_number"]
            street_address = loc["street_address_1"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal_code"]
            country_code = "CA"
            latitude = str(loc["latitude"])
            longitude = str(loc["longitude"])
            try:
                hours_of_operation = (
                    soup.find("div", {"class": "hours-wrapper office-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Office Hours", "")
                    + " "
                    + soup.find("div", {"class": "office-hours-note"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )

            except:
                hours_of_operation = MISSING
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
